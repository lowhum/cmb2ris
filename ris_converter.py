import re

class RobustRISConverter:
    def filter_valid_lines(self, text):
        return [line.strip() for line in text.strip().split('\n') if re.match(r'^([A-Z]{3,})', line.strip())]

    def extract_title(self, line):
        author_pattern = r'^[A-Z\-]+,\s+[A-Z][a-z]{0,2}\.(?:\s+et\s+al\.)?'
        match = re.match(author_pattern, line)
        if not match:
            return None
        remaining_text = line[match.end():].strip()
        # Extract text before the journal delimiter
        before_journal = remaining_text.split('//')[0]
        # Find positions of single (not double) slashes in this segment
        single_slash_positions = [i for i in range(len(before_journal))
            if before_journal[i] == '/' and
            (i == 0 or before_journal[i-1] != '/') and
            (i == len(before_journal) - 1 or before_journal[i+1] != '/')]
        # Take everything before last single slash, if one is present; else, use whole segment
        title_part = before_journal[:single_slash_positions[-1]].strip() if single_slash_positions else before_journal.strip()
        return title_part if title_part else None

    def extract_authors(self, line):
        before_journal = line.split('//')[0]
        single_slash_positions = [i for i in range(len(before_journal))
            if before_journal[i] == '/' and
            (i == 0 or before_journal[i-1] != '/') and
            (i == len(before_journal) - 1 or before_journal[i+1] != '/')]
        if single_slash_positions:
            last_slash = single_slash_positions[-1]
            author_part = before_journal[last_slash+1:].strip()
        else: return []
        names = [n.strip().rstrip('.') for n in author_part.split(',')]
        return [n for n in names if n and len(n) > 1]

    def extract_journal(self, line):
        m = re.search(r'//\s*([^,]+)', line)
        return m.group(1).strip() if m else None

    def extract_volume(self, line):
        m = re.search(r'//[^,]+,\s*([^\s,]+)', line)
        if m:
            val = m.group(1)
            if re.fullmatch(r'(19|20)\d{2}', val):
                return None
            if val.isdigit():
                return val
        return None

    def extract_year(self, line):
        parts = line.split('//', 1)
        if len(parts) < 2:
            return None
        after_journal = parts[1]
        m = re.search(r'\b(19|20)\d{2}\b', after_journal)
        if m:
            return m.group(0)
        return None

    def extract_issue(self, line):
        parts = line.split('//', 1)
        if len(parts) < 2:
            return None
        after_journal = parts[1]
        m = re.search(r',\s*N(?:o)?\.?\s*([^,]+)', after_journal)
        if m:
            return m.group(1).strip()
        return None

    def extract_issn(self, line):
        m = re.search(r'ISSN[\s:]+([0-9]{4}-[0-9]{3}[0-9Xx])', line)
        if m: return m.group(1).upper()
        return None

    def extract_pages(self, line):
        m = re.search(r'с\.\s*([\d-]+)', line)
        return m.group(1) if m else None

    def parse_line_to_ris(self, line):
        return {
            'TY': 'JOUR',
            'TI': self.extract_title(line),
            'AU': self.extract_authors(line),
            'JO': self.extract_journal(line),
            'VL': self.extract_volume(line),
            'PY': self.extract_year(line),
            'IS': self.extract_issue(line),
            'SN': self.extract_issn(line),
            'PG': self.extract_pages(line)
        }

    def format_ris_record(self, record):
        ris = [f"TY  - {record['TY']}"]
        if record['TI']: ris.append(f"TI  - {record['TI']}")
        if record['AU']:
            ris.extend([f"AU  - {a}" for a in record['AU'] if a])
        if record['JO']: ris.append(f"JO  - {record['JO']}")
        if record['VL']: ris.append(f"VL  - {record['VL']}")
        if record['PY']: ris.append(f"PY  - {record['PY']}")
        if record['IS']: ris.append(f"IS  - {record['IS']}")
        if record['SN']: ris.append(f"SN  - {record['SN']}")
        if record['PG']:
            pages = record['PG']
            if '-' in pages:
                try:
                    start_page, end_page = [x.strip() for x in pages.split('-')]
                    if start_page: ris.append(f"SP  - {start_page}")
                    if end_page: ris.append(f"EP  - {end_page}")
                except ValueError:
                    ris.append(f"SP  - {pages.strip()}")
            else:
                ris.append(f"SP  - {pages.strip()}")
        ris.append("ER  - ")
        return '\n'.join(ris)

    def process_text_to_ris(self, text):
        valid = self.filter_valid_lines(text)
        if not valid: return "No valid bibliographic entries found."
        out = []
        for line in valid:
            record = self.parse_line_to_ris(line)
            out.append(self.format_ris_record(record))
        return '\n\n'.join(out)
