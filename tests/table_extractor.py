import ast


# Define a visitor class to traverse the AST and extract table names
class TableNameExtractor(ast.NodeVisitor):
    def __init__(self):
        self.table_names = []

    def visit_ClassDef(self, node):
        if table_name := next(
            (
                statement.value.s
                for statement in node.body
                if isinstance(statement, ast.AnnAssign)
                and (
                    isinstance(statement.target, ast.Name)
                    and statement.target.id == "__tablename__"
                    and isinstance(statement.value, ast.Str)
                )
            ),
            None,
        ):
            self.table_names.append(table_name)
        self.generic_visit(node)
