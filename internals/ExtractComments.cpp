/// Clang tool for extracting comments from C++ code.
/// Based on:
/// https://gist.github.com/daniel-beard?page=1
/// Thanks to Daniel Beard.

#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendAction.h"
#include "clang/Lex/PreprocessorOptions.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "llvm/Support/CommandLine.h"
#include <iostream>

using namespace clang::tooling;
using namespace llvm;
using namespace clang;

class FindCommentsConsumer : public clang::ASTConsumer {
public:
  explicit FindCommentsConsumer(ASTContext * /* Context */) {}

  virtual void HandleTranslationUnit(clang::ASTContext &Context) {
    const std::map<unsigned, RawComment *> *commentsBySourceLoc =
        Context.getRawCommentList().getCommentsInFile(
            Context.getSourceManager().getMainFileID());
    for (auto commentAndSourceLoc : *commentsBySourceLoc) {
      const clang::RawComment &comment = *commentAndSourceLoc.second;
      // Don't bother with:
      // comment.isAttached()
      // it's always false.
      std::cout << comment.getRawText(Context.getSourceManager()).str()
                << std::endl;
    }
  }
};

class FindCommentsAction : public clang::ASTFrontendAction {
public:
  virtual std::unique_ptr<clang::ASTConsumer>
  CreateASTConsumer(clang::CompilerInstance &Compiler,
                    llvm::StringRef /*InFile*/) {
    // Ignore includes, and ignore all the resulting errors. We just want to
    // slurp up comments from this one file.
    Compiler.getPreprocessorOpts().SingleFileParseMode = true;
    Compiler.getDiagnostics().setClient(new IgnoringDiagConsumer());
    return std::unique_ptr<clang::ASTConsumer>(
        new FindCommentsConsumer(&Compiler.getASTContext()));
  }
};

static llvm::cl::OptionCategory MyToolCategory("extract-comments Options");
static cl::extrahelp CommonHelp(CommonOptionsParser::HelpMessage);
static cl::extrahelp MoreHelp("\nExtracts comments from specified source file.\n\nYou can invoke this tool if you want I guess, but it's intended for internal use by the spell-check.py script.");
int main(int argc, const char **argv) {
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());
  return Tool.run(newFrontendActionFactory<FindCommentsAction>().get());
}
