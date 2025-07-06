import logging
import pandas as pd
from typing import List, Dict, Any


def load_excel(file_path: str) -> Dict[str, Any]:
    try:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names

        result = {
            'content': '',
            'metadata': {
                'sheet_names': sheet_names,
                'num_sheets': len(sheet_names)
            },
            'sheets': []
        }

        all_sheets_content = []

        for sheet_name in sheet_names:
            try:
                # 尝试读取前1000行（避免内存溢出）
                df = xls.parse(sheet_name, nrows=1000)

                # 处理空表
                if df.empty:
                    sheet_content = f"[工作表 '{sheet_name}']\n空表"
                else:
                    # 获取基本统计信息
                    sheet_stats = {
                        'rows': len(df),
                        'columns': list(df.columns),
                        'dtypes': {col: str(df[col].dtype) for col in df.columns}
                    }

                    # 转换为CSV格式（保留结构）
                    csv_content = df.to_csv(sep='\t', na_rep='nan')

                    sheet_content = (
                        f"[工作表 '{sheet_name}']\n"
                        f"行数: {sheet_stats['rows']}\n"
                        f"列名: {', '.join(sheet_stats['columns'])}\n\n"
                        f"{csv_content}"
                    )

                all_sheets_content.append(sheet_content)
                result['sheets'].append({
                    'name': sheet_name,
                    'stats': sheet_stats,
                    'preview': csv_content[:500]  # 前500个字符预览
                })

            except Exception as e:
                logging.error(f"Error parsing sheet {sheet_name} in {file_path}: {str(e)}")
                all_sheets_content.append(f"[工作表 '{sheet_name}']\n解析错误: {str(e)}")

        result['content'] = "\n\n\n".join(all_sheets_content)
        result['size'] = len(result['content'])
        result['status'] = 'success'

        return result

    except Exception as e:
        logging.error(f"Error loading Excel {file_path}: {str(e)}")
        return {
            'content': f"Error: {str(e)}",
            'metadata': {},
            'sheets': [],
            'size': 0,
            'status': 'error'
        }
