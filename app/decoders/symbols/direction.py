from app.decoders.symbols.models import SymbolItem


class DirectionAnalyzer:
    def sort_symbols(self, symbols: list[SymbolItem], direction: str) -> list[SymbolItem]:
        '''
        Sorts symbols according to standard reading directions.
        '''
        if not symbols:
            return []
            
        direction = direction.lower()
        sorted_syms = []
        
        if direction in ["lr", "rl"]:
            syms = sorted(symbols, key=lambda s: s.bbox.center[1])
            rows = []
            current_row = [syms[0]]
            row_threshold = syms[0].bbox.h * 0.8
            
            for s in syms[1:]:
                if abs(s.bbox.center[1] - current_row[0].bbox.center[1]) < row_threshold:
                    current_row.append(s)
                else:
                    rows.append(current_row)
                    current_row = [s]
                    row_threshold = s.bbox.h * 0.8
            rows.append(current_row)
            
            for row in rows:
                if direction == "lr":
                    row_sorted = sorted(row, key=lambda s: s.bbox.center[0])
                else:
                    row_sorted = sorted(row, key=lambda s: s.bbox.center[0], reverse=True)
                sorted_syms.extend(row_sorted)
                
        elif direction in ["tb", "bt"]:
            syms = sorted(symbols, key=lambda s: s.bbox.center[0])
            cols = []
            current_col = [syms[0]]
            col_threshold = syms[0].bbox.w * 0.8
            
            for s in syms[1:]:
                if abs(s.bbox.center[0] - current_col[0].bbox.center[0]) < col_threshold:
                    current_col.append(s)
                else:
                    cols.append(current_col)
                    current_col = [s]
                    col_threshold = s.bbox.w * 0.8
            cols.append(current_col)
            
            for col in cols:
                if direction == "tb":
                    col_sorted = sorted(col, key=lambda s: s.bbox.center[1])
                else:
                    col_sorted = sorted(col, key=lambda s: s.bbox.center[1], reverse=True)
                sorted_syms.extend(col_sorted)
                
        else:
            sorted_syms = symbols
            
        return sorted_syms

direction_analyzer = DirectionAnalyzer()
