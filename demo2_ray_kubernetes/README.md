# Demo 2: Ray on Kubernetes

欢迎来到 Ray on Kubernetes 教程！这是 Hello Daft 系列的第二个 Demo。

## 📖 学习目标

通过本 Demo，你将学习：
- ✅ Ray 分布式计算框架的核心概念
- ✅ Ray Tasks 和 Actors 的使用
- ✅ 分布式并行计算实践
- ✅ 在 Kubernetes 上部署 Ray 集群
- ✅ 使用 KubeRay Operator 管理集群
- ✅ Ray Dashboard 监控和调试
- ✅ 实战：分布式图像处理

## 🎯 适合人群

- 了解 Python 基础的开发者
- 需要进行并行计算的工程师
- 对分布式系统感兴趣的学习者
- 希望在 Kubernetes 上部署应用的开发者

## ⏱️ 预计学习时间

- **快速浏览**: 2-3 小时
- **深入学习**: 2-3 天
- **完成 K8s 部署**: 额外 1-2 天

## 📚 内容结构

### Notebook 教程

1. **01_ray_basics.ipynb** - Ray 基础
   - Ray 核心概念
   - 本地 Ray 集群
   - 第一个 Ray 程序
   - Tasks vs Actors

2. **02_distributed_computing.ipynb** - 分布式计算
   - 并行数据处理
   - 资源管理
   - 错误处理和重试
   - 性能优化

3. **03_kubernetes_deployment.ipynb** - Kubernetes 部署
   - KubeRay Operator 介绍
   - 部署 Ray 集群
   - 连接和使用集群
   - 监控和调试

## 🚀 快速开始

### 前置要求

**本地开发**：
- Python 3.10+
- 至少 8GB 内存

**Kubernetes 部署**：
- Kubernetes 集群（minikube/kind/k3s 或云端）
- kubectl 已安装并配置
- Helm 3.x（可选）

### 1. 本地 Ray 实验

```bash
cd demo2_ray_kubernetes

# 安装依赖
pip install -r ../requirements.txt

# 启动 Jupyter
jupyter notebook notebooks/01_ray_basics.ipynb
```

### 2. Kubernetes 环境准备

#### 选项 A: 使用 minikube（推荐本地测试）

```bash
# 安装 minikube
# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# 启动集群（需要至少 8GB 内存）
minikube start --cpus=4 --memory=8192 --disk-size=50g

# 验证
kubectl get nodes
```

#### 选项 B: 使用 kind

```bash
# 安装 kind
go install sigs.k8s.io/kind@latest

# 创建集群
kind create cluster --name ray-demo --config k8s/kind-config.yaml

# 验证
kubectl cluster-info
```

#### 选项 C: 使用云端 K8s（GKE/EKS/AKS）

参考各云平台文档创建集群。

### 3. 部署 Ray 集群

```bash
# 运行自动化部署脚本
./scripts/deploy_ray.sh

# 或手动部署
kubectl create namespace ray-system
kubectl apply -f k8s/ray-operator.yaml
kubectl apply -f k8s/ray-cluster.yaml

# 检查部署状态
kubectl get rayclusters -n ray-system
kubectl get pods -n ray-system
```

### 4. 访问 Ray Dashboard

```bash
# 端口转发
kubectl port-forward -n ray-system service/ray-cluster-head-svc 8265:8265

# 在浏览器中打开
# http://localhost:8265
```

## 💡 核心概念

### 1. Ray Tasks

Tasks 是无状态的远程函数，适合并行计算。

```python
import ray

ray.init()

@ray.remote
def process_data(data):
    # 处理数据
    return result

# 并行执行
futures = [process_data.remote(d) for d in data_list]
results = ray.get(futures)
```

**特点**：
- 无状态
- 自动并行
- 容错重试
- 适合 ETL、数据处理

### 2. Ray Actors

Actors 是有状态的分布式对象，适合需要维护状态的场景。

```python
@ray.remote
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self.count

# 创建 actor
counter = Counter.remote()

# 调用方法
result = ray.get(counter.increment.remote())
```

**特点**：
- 有状态
- 方法调用
- 并发控制
- 适合服务、缓存

### 3. 资源管理

Ray 支持细粒度的资源管理：

```python
# 指定 CPU 资源
@ray.remote(num_cpus=2)
def cpu_intensive_task():
    pass

# 指定 GPU 资源
@ray.remote(num_gpus=1)
def gpu_task():
    pass

# 指定内存
@ray.remote(memory=1000 * 1024 * 1024)  # 1GB
def memory_intensive_task():
    pass
```

### 4. KubeRay Operator

KubeRay 是 Kubernetes Operator，用于管理 Ray 集群：

- 自动化部署和扩缩容
- 健康检查和自愈
- 资源管理
- 多集群支持

## 📊 实战示例：分布式图像处理

### 场景描述

处理 10,000 张图片：
- 调整大小（resize）
- 格式转换（PNG → JPEG）
- 添加水印
- 保存到输出目录

### 串行处理 vs Ray 并行处理

```python
import ray
from PIL import Image
import time

# 串行处理
def process_image_serial(image_path):
    img = Image.open(image_path)
    img = img.resize((800, 600))
    img.save(f"output/{image_path.name}")

start = time.time()
for img_path in image_paths:
    process_image_serial(img_path)
print(f"串行耗时: {time.time() - start:.2f}s")

# Ray 并行处理
@ray.remote
def process_image_parallel(image_path):
    img = Image.open(image_path)
    img = img.resize((800, 600))
    img.save(f"output/{image_path.name}")

ray.init()
start = time.time()
futures = [process_image_parallel.remote(p) for p in image_paths]
ray.get(futures)
print(f"并行耗时: {time.time() - start:.2f}s")
```

**性能对比**（10K 图片）：
- 串行处理：~300 秒
- Ray 并行（4 核）：~80 秒
- Ray 并行（8 核）：~45 秒

## 🏗️ Kubernetes 架构

### Ray 集群组件

```
┌─────────────────────────────────────────┐
│         Kubernetes Namespace            │
│                                         │
│  ┌───────────────────────────────┐    │
│  │      Ray Head Node            │    │
│  │  - Scheduler                  │    │
│  │  - GCS (Global Control Store) │    │
│  │  - Dashboard (8265)           │    │
│  │  - Client Server (10001)      │    │
│  └───────────────────────────────┘    │
│              │                          │
│              ▼                          │
│  ┌───────────────────────────────┐    │
│  │      Ray Worker Nodes         │    │
│  │  ┌─────────┐  ┌─────────┐    │    │
│  │  │Worker 1 │  │Worker 2 │    │    │
│  │  └─────────┘  └─────────┘    │    │
│  │  ┌─────────┐  ┌─────────┐    │    │
│  │  │Worker 3 │  │Worker 4 │    │    │
│  │  └─────────┘  └─────────┘    │    │
│  └───────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

### 资源配置

**Head Node**：
- CPU: 2 核
- Memory: 4Gi
- 端口: 8265 (Dashboard), 10001 (Client), 6379 (Redis)

**Worker Nodes**：
- 副本数: 3-5（可自动扩缩容）
- CPU: 4 核/节点
- Memory: 8Gi/节点

## 🎓 练习题

### 初级练习

1. **Hello Ray**
   - 编写第一个 Ray Task
   - 并行计算斐波那契数列
   - 测量加速比

2. **Ray Actors**
   - 实现分布式计数器
   - 创建简单的 Key-Value 存储
   - 测试并发访问

3. **资源管理**
   - 指定不同的资源需求
   - 观察任务调度
   - 处理资源不足的情况

### 中级练习

4. **数据处理管道**
   - 并行读取多个文件
   - 分布式数据转换
   - 聚合结果

5. **错误处理**
   - 实现任务重试逻辑
   - 处理部分失败
   - 超时控制

6. **性能优化**
   - 对比不同并行度的性能
   - 优化数据传输
   - 减少序列化开销

### 高级练习

7. **Kubernetes 部署**
   - 部署 Ray 集群到 K8s
   - 配置自动扩缩容
   - 监控集群状态

8. **分布式应用**
   - 实现分布式爬虫
   - 构建实时数据处理管道
   - 集成外部服务

9. **生产化**
   - 添加日志和监控
   - 实现优雅关闭
   - 配置资源限制

## 🐛 常见问题

### Q1: Ray 初始化失败

```python
# 检查 Ray 是否已经运行
ray.is_initialized()

# 如果已运行，先关闭
ray.shutdown()

# 重新初始化
ray.init()
```

### Q2: 连接 K8s 上的 Ray 集群

```python
import ray

# 获取 Ray Head 地址
# kubectl get svc -n ray-system

# 连接到集群
ray.init(address="ray://ray-cluster-head-svc:10001")
```

### Q3: KubeRay Operator 安装失败

```bash
# 检查 CRD
kubectl get crd | grep ray

# 重新安装
kubectl delete -f k8s/ray-operator.yaml
kubectl apply -f k8s/ray-operator.yaml

# 查看日志
kubectl logs -n ray-system -l app.kubernetes.io/name=kuberay-operator
```

### Q4: Worker 节点无法启动

```bash
# 检查资源
kubectl describe nodes

# 检查 Pod 状态
kubectl describe pod -n ray-system <worker-pod-name>

# 可能需要调整资源请求
# 编辑 k8s/ray-cluster.yaml
```

## 📚 参考资源

### 官方文档
- [Ray 官方文档](https://docs.ray.io/)
- [Ray Core API](https://docs.ray.io/en/latest/ray-core/walkthrough.html)
- [KubeRay 文档](https://docs.ray.io/en/latest/cluster/kubernetes/index.html)
- [Ray Dashboard](https://docs.ray.io/en/latest/ray-observability/getting-started.html)

### 示例代码
- [Ray Examples](https://github.com/ray-project/ray/tree/master/python/ray/examples)
- [KubeRay Examples](https://github.com/ray-project/kuberay/tree/master/ray-operator/config/samples)

### 社区
- [Ray Slack](https://forms.gle/9TSdDYUgxYs8SA9e8)
- [Ray Discourse](https://discuss.ray.io/)
- [GitHub Issues](https://github.com/ray-project/ray/issues)

## ✅ 完成检查清单

完成本 Demo 后，你应该能够：

- [ ] 理解 Ray 的核心概念（Tasks、Actors）
- [ ] 编写并行计算程序
- [ ] 使用 Ray 进行分布式数据处理
- [ ] 管理计算资源
- [ ] 在本地运行 Ray 集群
- [ ] 在 Kubernetes 上部署 Ray 集群
- [ ] 使用 Ray Dashboard 监控任务
- [ ] 处理分布式计算中的错误
- [ ] 优化 Ray 应用性能
- [ ] 完成至少 3 个练习题

## 🎯 下一步

完成本 Demo 后，继续学习：

👉 [Demo 3: LanceDB 基础](../demo3_lancedb_basics/) - 学习向量数据库和语义搜索

---

**祝学习愉快！** 🚀

如有问题，请查看 [故障排除指南](../docs/troubleshooting.md) 或提交 [Issue](https://github.com/your-username/hello_daft/issues)。
