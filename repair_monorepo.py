import os
from pathlib import Path
import re

def repair_file(path):
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Could not read {path}: {e}")
        return False
    
    original = content
    
    # 1. Fix literal newlines in strings/chars
    # We search for a quote/tick followed by a newline where it should be escaped
    # This is tricky because content might use \r\n or \n
    content = content.replace('message.dump() + "\n";', 'message.dump() + "\\n";')
    content = content.replace('message.dump() + "\r\n";', 'message.dump() + "\\n";')
    content = content.replace('j.dump() + "\n";', 'j.dump() + "\\n";')
    content = content.replace('j.dump() + "\r\n";', 'j.dump() + "\\n";')
    content = content.replace("buffer.find('\n')", "buffer.find('\\n')")
    content = content.replace("buffer.find('\r\n')", "buffer.find('\\n')")
    content = content.replace("buffer[0] == '\n'", "buffer[0] == '\\n'")
    content = content.replace("buffer[0] == '\r\n'", "buffer[0] == '\\n'")
    content = content.replace("data.push('\n');", "data.push('\\n');")
    content = content.replace("data.push('\r\n');", "data.push('\\n');")
    
    # 2. C++ Fixes
    # MOCK_METHOD parentheses fix
    content = content.replace('MOCK_METHOD((std::map<std::string, Security>), get_securities, (), (override));', 
                              'MOCK_METHOD((std::map<std::string, Security>), get_securities, (), (override));')
    content = content.replace('MOCK_METHOD((std::vector<News>), get_news, (int), (override));',
                              'MOCK_METHOD((std::vector<News>), get_news, (int), (override));')
    
    # Direction::BUY fix
    content = content.replace('Direction::BUY', 'Direction::BUY')
    content = content.replace('Direction::SELL', 'Direction::SELL')

    # 3. Rust Fixes
    # rand 0.9 compatibility
    if path.suffix == '.rs':
        if 'rand_distr::Normal' in content and 'use rand_distr::Distribution' not in content:
            content = content.replace('use rand_distr::Normal;', 'use rand_distr::{Normal, Distribution};')
        if 'StdRng::seed_from_u64' in content and 'use rand::SeedableRng' not in content:
            content = "use rand::SeedableRng;\n" + content
        if '.sample(&mut rng)' in content and 'use rand::Rng' not in content:
            if 'use rand::' in content:
                content = content.replace('use rand::', 'use rand::{Rng, ')
            elif 'use rand::prelude::*' in content:
                content = content.replace('use rand::prelude::*;', 'use rand::prelude::*;\nuse rand::Rng;')
            else:
                content = "use rand::Rng;\n" + content

    if content != original:
        path.write_text(content, encoding='utf-8')
        return True
    return False

if __name__ == "__main__":
    count = 0
    ignore_dirs = {".github", "docs", "bazel-", ".git", "technical_specification", "node_modules"}
    for p in Path('.').rglob('*'):
        if p.is_file() and p.suffix in ['.cpp', '.hpp', '.h', '.rs', '.py']:
            if any(part in ignore_dirs for part in p.parts):
                continue
            if repair_file(p):
                print(f"Repaired {p}")
                count += 1
    print(f"Total files repaired: {count}")
