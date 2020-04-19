from cmp.utils import Token, tokenizer

def get_lexer(G, ll1):
    fixed_tokens = { t.Name: Token(t.Name, t) for t in G.terminals if t not in { G["id"], G["int"]  }}

    @tokenizer(G, fixed_tokens)
    def tokenize_text(token):
        lex = token.lex
        try:
            float(lex)
            return token.transform_to( G["int"] )
        except ValueError:
            return token.transform_to(G["id"])

    return tokenize_text

