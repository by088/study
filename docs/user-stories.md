# 全量用户故事（阶段二基线）

## 学生端

### US-01 注册账号
As a 学生, I want to 注册账号, so that 我可以使用预约系统。
- Given 学号未注册
- When 提交合法信息
- Then 创建账号成功并可登录

### US-02 登录系统
As a 学生, I want to 登录, so that 我可以查看和预约座位。
- Given 账号密码正确
- When 发起登录
- Then 返回认证信息

### US-03 查询可用自习室
As a 学生, I want to 查询可用自习室, so that 我可以选择学习地点。
- Given 系统有可用教室
- When 按校区/楼宇/标签筛选
- Then 返回符合条件的自习室列表

### US-04 查询某时段座位状态
As a 学生, I want to 查询某时段座位状态, so that 我可以快速选座。
- Given 选择了教室和开始时间
- When 查询座位状态
- Then 返回每个座位可预约时长和标签

### US-05 提交预约
As a 学生, I want to 预约座位, so that 我能获得学习席位。
- Given 信用分 >= 60 且时间规则合法
- When 提交预约
- Then 生成待生效预约记录

### US-06 取消预约
As a 学生, I want to 取消未生效预约, so that 我能释放资源。
- Given 预约状态为待生效
- When 发起取消
- Then 预约置为已取消并释放座位

### US-07 签到
As a 学生, I want to 通过签到码签到, so that 预约生效。
- Given 在签到窗口内且验证码正确
- When 发起签到
- Then 预约状态变为已生效

### US-08 查看历史并复订
As a 学生, I want to 查看历史并一键复订, so that 减少重复操作。
- Given 存在历史预约
- When 点击复订
- Then 自动带入座位和时段进行新预约校验

## 管理端（RBAC）

### US-09 角色管理
As a 管理员, I want to 管理角色, so that 权限边界清晰。
- Given 我有角色管理权限
- When 新增/编辑/禁用角色
- Then 角色状态生效

### US-10 用户授权
As a 管理员, I want to 给用户分配角色, so that 不同人看到不同功能。
- Given 角色已定义
- When 指定用户角色
- Then 用户权限即时更新

### US-11 教室管理
As a 管理员, I want to 管理自习室, so that 可维护开放资源。
- Given 我有教室管理权限
- When 新增/修改/停用教室
- Then 学生端查询结果同步变化

### US-12 座位管理
As a 管理员, I want to 管理座位, so that 维护座位标签和可用性。
- Given 我有座位管理权限
- When 新增/编辑/注销座位
- Then 座位状态更新

### US-13 预约记录管理
As a 管理员, I want to 查询预约记录, so that 可追踪运营情况。
- Given 我有预约查看权限
- When 按条件筛选
- Then 返回对应预约记录

### US-14 违约记录管理
As a 管理员, I want to 查询违约记录, so that 可执行管理策略。
- Given 我有违约查看权限
- When 按用户/日期筛选
- Then 返回违约明细

### US-15 系统参数管理
As a 管理员, I want to 调整系统参数, so that 业务规则可配置。
- Given 我有参数管理权限
- When 修改最大预约时长等参数
- Then 新规则对后续预约生效

## 系统自动化

### US-16 预约前提醒
As a 系统, I want to 在预约前15分钟提醒, so that 降低爽约率。
- Given 当前时刻命中提醒窗口
- When 任务触发
- Then 向待生效用户发送提醒

### US-17 预约后未签到提醒
As a 系统, I want to 在开始后10分钟二次提醒, so that 提醒用户及时签到。
- Given 用户仍未签到
- When 到达开始后10分钟
- Then 发送二次提醒

### US-18 预约超时违约处理
As a 系统, I want to 在开始后15分钟自动违约处理, so that 释放资源并惩戒。
- Given 用户未签到
- When 到达开始后15分钟
- Then 标记违约、释放座位、扣减信用并记录违约日志

### US-19 自动结束预约
As a 系统, I want to 到点结束预约, so that 状态与实际一致。
- Given 预约已生效
- When 超过预约结束时间
- Then 状态改为已结束

## DevOps 与协作

### US-20 CI 自动构建测试
As a 开发团队, I want to 提交即触发构建测试, so that 快速发现问题。
- Given 代码提交仓库
- When CI触发
- Then 完成lint/单测/接口测并产出报告

### US-21 Test 自动部署
As a 开发团队, I want to 测试环境自动部署, so that 快速验证迭代。
- Given CI通过
- When 进入部署阶段
- Then 自动发布到Test

### US-22 Prod 审批发布
As a 负责人, I want to 生产发布需审批, so that 控制发布风险。
- Given Test验证通过
- When 审批通过
- Then 发布到Prod
