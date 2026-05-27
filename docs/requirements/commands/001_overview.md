# fastai commands overview

## 项目相关命令


### fastai recon

Project reconnaissance.  
快速过一遍当前项目的文档、代码中的模块结构，以便对当前项目有一个整体全局的理解（不追求理解细节）。 
并整理成`系统概要文档`保存到文件中。

### fastai init

把当前目录初始化为 AI-ready 项目。

职责：
- 识别仓库类型与现状  
- 写入 FastAI 所需的项目元数据和目录结构  
- 生成初始 rules / memory / workflow / docs scaffold  


### fastai sync

对当前项目执行一次显式同步。

职责：
- 对比代码、文档、规则、memory 的变动  
- 更新派生 AI 资产  
- 修正过期的索引/摘要/上下文  
- 必要时给出变更建议或生成 patch 预览  

它是手动触发版的“maintenance loop”

## FastAI 服务相关命令

### fastai serve

启动本机 FastAI 守护进程；如果已运行，则做健康检查并提示复用。

职责：
- 启动用户级后台服务  
- 建立本机 socket / pid / state / logs  
- 暴露给项目命令调用的统一服务端能力  


### fastai status

显示当前 FastAI 系统状态。  

显示: 
- 守护进程是否运行
- 监听地址
- 版本
- 最近活动时间
- 已连接项目数/列表

### fastai logs

查看与当前项目或 daemon 相关日志。


### fastai stop

