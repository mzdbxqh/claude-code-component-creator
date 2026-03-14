"""
性能基准测试

作者: mzdbxqh
创建时间: 2026-03-14
"""
import sys
import time
sys.path.append('..')

from reference_scanner import validate_references, build_dependency_graph, detect_cycles

def benchmark_plugin(plugin_dir, name):
    """基准测试单个插件"""
    print(f"\n{'='*60}")
    print(f"基准测试: {name}")
    print(f"{'='*60}")

    start = time.time()
    results = validate_references(plugin_dir)
    scan_time = time.time() - start

    start = time.time()
    graph = build_dependency_graph(plugin_dir)
    graph_time = time.time() - start

    start = time.time()
    cycles = detect_cycles(graph)
    cycle_time = time.time() - start

    total_time = scan_time + graph_time + cycle_time

    print(f"扫描时间: {scan_time:.3f}s")
    print(f"图构建时间: {graph_time:.3f}s")
    print(f"循环检测时间: {cycle_time:.3f}s")
    print(f"总时间: {total_time:.3f}s")
    print(f"断开引用: {len(results['broken_references'])}")
    print(f"孤儿文件: {len(results['orphan_files'])}")
    print(f"循环数: {len(cycles)}")

    return total_time

if __name__ == '__main__':
    benchmarks = [
        ('../../test-fixtures/reference-integrity/valid-plugin', '正常插件 (3组件)'),
        ('../../test-fixtures/reference-integrity/broken-refs', '断开引用 (1组件)'),
        ('../../test-fixtures/reference-integrity/orphans', '孤儿文件 (3组件)'),
        ('../../test-fixtures/reference-integrity/circular', '循环引用 (3组件)'),
    ]

    times = []
    for plugin_dir, name in benchmarks:
        t = benchmark_plugin(plugin_dir, name)
        times.append(t)

    print(f"\n{'='*60}")
    print(f"平均时间: {sum(times)/len(times):.3f}s")
    print(f"最快: {min(times):.3f}s")
    print(f"最慢: {max(times):.3f}s")
    print(f"{'='*60}")
