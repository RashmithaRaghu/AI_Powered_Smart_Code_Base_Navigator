# build.py
from tree_sitter import Language

# This command tells Tree-sitter to compile the grammars found in the 'vendor'
# folder and create a single library file in the 'build' folder.
Language.build_library(
  'build/my-languages.so',
  [
    'vendor/tree-sitter-python',
  ]
)
print("✅ Tree-sitter grammar library built successfully!")