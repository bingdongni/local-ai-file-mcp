import argparse
import logging
import json
from src.document_processor import DocumentProcessor


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    setup_logging()
    parser = argparse.ArgumentParser(description='文件索引与检索工具')
    subparsers = parser.add_subparsers(dest='command')

    # 索引命令
    index_parser = subparsers.add_parser('index', help='索引文件或目录')
    index_parser.add_argument('--file', help='单个文件路径')
    index_parser.add_argument('--dir', help='目录路径')
    index_parser.add_argument('--ext', nargs='+', help='文件扩展名，如 .txt .pdf')

    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索索引')
    search_parser.add_argument('--query', required=True, help='搜索查询')
    search_parser.add_argument('--count', type=int, default=3, help='返回结果数量')

    # 统计命令
    subparsers.add_parser('count', help='获取索引文档数量')

    args = parser.parse_args()
    processor = DocumentProcessor()

    if args.command == 'index':
        if args.file:
            result = processor.process_file(args.file)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.dir:
            results = processor.process_directory(args.dir, args.ext)
            print(f"已处理 {len(results)} 个文件")
            errors = [r for r in results if r['status'] == 'error']
            if errors:
                print(f"错误: {len(errors)} 个文件处理失败")
        else:
            print("请指定 --file 或 --dir 参数")

    elif args.command == 'search':
        from src.indexer.chroma_index import search
        results = search(processor.collection, args.query, args.count)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.command == 'count':
        count = processor.get_document_count()
        print(f"索引中的文档数量: {count}")


if __name__ == "__main__":
    main()
