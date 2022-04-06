# account.py
有关账户所有操作，被封装在了此文件的Account类中，使用方式如下：

类创建：

需传入参数captial ，即账户初始本金



属性：

self.asset    —— 资产详情 (日期、总资产、现金、股票资产、收益、收益率)

self.position —— 持   仓 （日期、股票代码、持仓市值、持仓数量、成本价、持仓收益、持仓收益率）

self.order    —— 订单记录 （日期、交易方式 B/S、股票代码、交易数量、交易价格）



方法：

self.no_trade_update_asset

当没有交易发生时，调用此方法，实现对资产详情（self.asset）的更新，需传入参数 ：date, symbol, price （日期、股票代码、股票最新收盘价）



self.trade_update

当发生交易时，调用此方法，实现对订单记录、持仓、资产详情的更新，需传入参数：date, trade_type, symbol, amount, trade_price（日期、交易类型 B/S、股票代码、交易数量、交易价格）



plot_profit_rate

调用此方法，绘制 self.asset 的收益率曲线

# quan_trade.py
里面有很多的交易策略，我们将历史行情数据丢给它，它会自动计算出相应的各种指标（均线、布林带等），再根据我们选定的策略、每次交易数量、账户本金等，反馈给我们操作后的账户详情。

+ 类创建需传入的参数：
  - symbol，交易股票的代码
  - data， 该股票的历史行情数据（DataFrame，其字段名需满足一定规范）
  - trade_amount， 交易数量
  - trade_strategy， 交易策略（boll、mean ...）
  - capital, 初始本金
  - start_date， 开始日期
  - end_date， 截止日期

+ 方法：
  - self.main ——  调用此方法，会根据选定的策略更新账户所有相关数据

+ 属性：
    + self.account  —— Account的实列化对象，具备其所有的属性及方法
  
      - self.account.asset    —— 资产详情 (日期、总资产、现金、股票资产、收益、收益率)

      - self.account.position —— 持   仓 （日期、股票代码、持仓市值、持仓数量、成本价、持仓收益、持仓收益率）

      - self.account.order    —— 订单记录 （日期、交易方式 B/S、股票代码、交易数量、交易价格）
      
      - self.account.plot_profit_rate  —— 调用此方法，绘制 self.account.asset 的收益率曲线


**二者会不断更新迭代，文件始终会保持为最新版本**
