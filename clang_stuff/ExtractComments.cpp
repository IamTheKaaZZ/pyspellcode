/// Clang tool for extracting comments from C++ code.
/// Based on:
/// https://gist.github.com/daniel-beard?page=1
/// Thanks to Daniel Beard.

#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendAction.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "llvm/Support/CommandLine.h"
#include <iostream>

using namespace clang::tooling;
using namespace llvm;
using namespace clang;

class FindCommentsConsumer : public clang::ASTConsumer {
public:
  explicit FindCommentsConsumer(ASTContext *Context) {}

  virtual void HandleTranslationUnit(clang::ASTContext &Context) {
    const std::map<unsigned, RawComment *> *commentsBySourceLoc =
        Context.getRawCommentList().getCommentsInFile(
            Context.getSourceManager().getMainFileID());
    std::cout << "Comments in translation unit:";
    for (auto commentAndSourceLoc : *commentsBySourceLoc) {
      const clang::RawComment &comment = *commentAndSourceLoc.second;
      // std::cout << comment->getBriefText(Context.getSourceManager()) <<
      // std::endl;
      std::cout << comment.getRawText(Context.getSourceManager()).str()
                << std::endl;
    }
    std::cout << "Finished parsing for comments." << std::endl;
  }
};

class FindCommentsAction : public clang::ASTFrontendAction {
public:
  // FindCommentsAction() {
  //   getCompilerInstance().getPreprocessorOpts.SingleFileParseMode = true;
  // }

  virtual std::unique_ptr<clang::ASTConsumer>
  CreateASTConsumer(clang::CompilerInstance &Compiler, llvm::StringRef InFile) {
    return std::unique_ptr<clang::ASTConsumer>(
        new FindCommentsConsumer(&Compiler.getASTContext()));
  }
};

static llvm::cl::OptionCategory MyToolCategory("My tool options");
int main(int argc, const char **argv) {
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());
  return Tool.run(newFrontendActionFactory<FindCommentsAction>().get());
}
