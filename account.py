


"""
Account类，实现对账户的管理
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Account(object):
	"""docstring for  Account"""
	def __init__(self, capital):
		# capital 账户初始本金 
		self.capital = capital
		self.init_account()

	def init_account(self):
		## 初始化账户
		# 资产详情 (日期、总资产、现金、股票资产、收益、收益率)
		self.asset = pd.DataFrame(
			columns = ['date','total', 'cash', 'stock', 'profit', 'profit_rate'])
		self.asset = self.asset.append({
			'date' : np.nan,
			'total' : self.capital, 
			'cash' : self.capital, 
			'stock' : 0, 
			'profit' : 0, 
			'profit_rate' : 0
			}, ignore_index = True)
		# 持仓 （日期、股票代码、持仓市值、持仓数量、成本价、持仓收益、持仓收益率
		self.position = pd.DataFrame(columns = ['date','symbol', 'stock_value', 'amount', 'buy_price', 'profit', 'profit_rate'])
		# 订单记录 （日期、交易方式 B/S、股票代码、交易数量、交易价格）
		self.order = pd.DataFrame(columns = ['date', 'trade_type', 'symbol', 'amount', 'trade_price'])

	def trade_update(self, date, trade_type, symbol, amount, trade_price):
		### 发生交易后，更新订单记录、持仓、资产
		## 更新订单记录
		self.order = self.order.append({
			'date':date,
			'trade_type': trade_type, 
			'symbol': symbol, 
			'amount': amount,
			'trade_price': trade_price
			}, ignore_index = True)

		# 判断交易方式,给数量添加正负号
		amount = amount if trade_type == 'B' else ( -1 * amount)

		## 更新持仓
		# 已有该股票的持仓记录
		if symbol in self.position['symbol'].values :
			self.position = self.position.append({
				'date': date,
	            'symbol': symbol, 
	            'stock_value' :  (self.position[self.position['symbol'] == symbol].iloc[-1].amount + amount) * trade_price ,
	            'amount' : self.position[self.position['symbol'] == symbol].iloc[-1].amount + amount,
	            'buy_price' : (self.position[self.position['symbol'] == symbol].iloc[-1].amount * self.position[self.position['symbol'] == symbol].iloc[-1].buy_price + amount * trade_price) / (self.position[self.position['symbol'] == symbol].iloc[-1].amount + amount) if (self.position[self.position['symbol'] == symbol].iloc[-1].amount + amount) != 0 else 0,
	            'profit' : (trade_price -((self.position[self.position['symbol'] == symbol].iloc[-1].amount * self.position[self.position['symbol'] == symbol].iloc[-1].buy_price + amount * trade_price) / (self.position[self.position['symbol'] == symbol].iloc[-1].amount + amount))) * (self.position[self.position['symbol'] == symbol].iloc[-1].amount + amount) if (self.position[self.position['symbol'] == symbol].iloc[-1].amount + amount) != 0 else 0,
	            'profit_rate' : ((trade_price / ((self.position[self.position['symbol'] == symbol].iloc[-1].amount * self.position[self.position['symbol'] == symbol].iloc[-1].buy_price + amount * trade_price) / (self.position[self.position['symbol'] == symbol].iloc[-1].amount + amount)) - 1 ) * 100) if (self.position[self.position['symbol'] == symbol].iloc[-1].amount + amount) != 0 else 0
	            } , ignore_index = True)
		# 第一次持仓该股票
		else:
			self.position = self.position.append({
				'date': date,
	            'symbol': symbol, 
	            'stock_value' : trade_price * amount,
	            'amount' : amount,  # 第一次持仓，交易方式只会是‘B’，故amount为正数
	            'buy_price' : trade_price,
	            'profit' : 0,
	            'profit_rate' :0,
	            } , ignore_index = True)

		## 更新资产
		self.asset = self.asset.append({
			'date' : date,
			'total': self.asset.iloc[-1].cash - amount * trade_price + self.position.iloc[-1].stock_value, 
			'cash' : self.asset.iloc[-1].cash - amount * trade_price, 
			'stock' : self.position.iloc[-1].stock_value,   # 目前只考虑持仓一只股票（多只持仓不适用）
			'profit' : (self.asset.iloc[-1].cash - amount * trade_price + self.position.iloc[-1].stock_value) - self.capital , 
			'profit_rate' : ((self.asset.iloc[-1].cash - amount * trade_price + self.position.iloc[-1].stock_value)/self.capital - 1) *100
			}, ignore_index = True)


	def no_trade_update_asset(self, date, symbol, price):
		### 无交易发生时，资产会随持仓股票波动，也需更新
		# 股票资产为0时
		if self.asset.iloc[-1].stock == 0 :
			self.asset = self.asset.append({
				'date' : date,
				'total' : self.asset.iloc[-1].total, 
				'cash' : self.asset.iloc[-1].cash, 
				'stock' : 0, 
				'profit' : self.asset.iloc[-1].total - self.capital, 
				'profit_rate' : (self.asset.iloc[-1].total / self.capital - 1) * 100,
				}, ignore_index = True)
		# 股票资产不为0时， 计算股票资产最新价格
		else : 
			self.asset = self.asset.append({
				'date' : date,
				'total' : self.asset.iloc[-1].cash + self.position[self.position['symbol'] == symbol].iloc[-1].amount * price, 
				'cash' : self.asset.iloc[-1].cash, 
				'stock' : self.position[self.position['symbol'] == symbol].iloc[-1].amount * price, 
				'profit' : self.asset.iloc[-1].cash + self.position[self.position['symbol'] == symbol].iloc[-1].amount * price - self.capital, 
				'profit_rate' : ((self.asset.iloc[-1].cash + self.position[self.position['symbol'] == symbol].iloc[-1].amount * price) / self.capital -1) * 100
				}, ignore_index = True)

	def plot_profit_rate(self):
		# 绘制收益率曲线
		if not self.asset.empty:
			plt.figure('profit_rate')
			plt.title('profit_·rate',fontsize = 18)
			plt.xlabel('date',fontsize = 14)
			plt.ylabel('rate', fontsize = 14)
			plt.grid(linestyle = ':')
			plt.plot(self.asset['date'], self.asset['profit_rate'])
			plt.show()






