# quan_trade.py

import pandas as pd
import akshare as ak
import numpy as np
import dateutil
import account #导入账户管理类

# 获取n日收盘均价
def get_ma(data, n):
	# 创建列 ‘ma(n)’
	ma = 'ma{}'.format(n)
	data[ma] = np.nan
	# 计算n日收盘均价并保存到data
	for i in range(n, data.shape[0]) :
		data[ma][i] = data['收盘'][i-n:i].mean()
	return data

# 获取布林带上下轨
def get_boll(data):
	data['upper'] = np.nan
	data['lower'] = np.nan
	# boll上下轨由20日均线计算得出
	for i in range(20,data.shape[0]):
	    data['upper'][i] = data['ma20'][i] + 2*data['收盘'][i-20:i].std()
	    data['lower'][i] = data['ma20'][i] - 2*data['收盘'][i-20:i].std()
	return data

class Trade:
	def __init__(self, symbol, data, trade_strategy, trade_amount = 100 , capital = 100000, start_date = '1900-01-01', end_date = '2099-01-01',max_volatility = None):
		self.symbol = symbol
		self.data = data
		self.trade_amount = trade_amount
		self.trade_strategy = trade_strategy
		self.capital = capital
		self.start_date = start_date
		self.end_date = end_date
		self.max_volatility = max_volatility
		# 初始化数据
		self.init_data()
		# 创建账户,并初始化asset
		self.account = account.Account(self.capital)

	def init_data(self):
		# 数据整理
		self.data['日期'] = pd.to_datetime(self.data['日期'])
		# 从指定日期前60日切片，是为了减少计算均线、布林带的范围，同时保证指定日期内的数据完整
		self.data = self.data[self.data['日期'] >= pd.to_datetime(self.start_date) - dateutil.relativedelta.relativedelta(days = 60)][self.data['日期'] <= pd.to_datetime(self.end_date)].reset_index(drop = True)
		# 分别获取ma5，ma10，ma20，ma30
		for i in (3,5,8,10,12,15,20,30,35,40,45,50,60):
			self.data = get_ma(self.data,i)
		# 获取boll上下轨
		self.data = get_boll(self.data)
		# 取出指定期间内的数据
		self.data = self.data[self.data['日期'] >= pd.to_datetime(self.start_date)].reset_index(drop = True)

	def if_limit_move(self,high,low,rise):
		# 有涨跌幅限制时，判断是否一字涨停或跌停
		if self.max_volatility:
			return True if high == low and rise >= self.max_volatility else False

	# def by_boll(self):
	# ## 跌破下轨买入，突破上轨清仓
	# 	for i in range(0, self.data.shape[0]):
	# 		# 如果当天一字涨停或者跌停，无需交易
	# 		if self.if_limit_move(self.data.iloc[i].最高, self.data.iloc[i].最低, self.data.iloc[i].涨跌幅):
	# 			self.account.no_trade_update_asset(self.data.iloc[i].日期, self.symbol, self.data.iloc[i].收盘)
	# 			continue

	# 		# 布林带数据为空无需判断买卖时，只需更新资产数据
	# 		if pd.isnull(self.data.iloc[i]['ma20']) :
	# 			self.account.no_trade_update_asset(self.data.iloc[i].日期, self.symbol, self.data.iloc[i].收盘)
	# 		else:
	# 			if self.data.iloc[i].收盘 < self.data.iloc[i].lower and (self.account.asset.iloc[-1].cash >= self.data.iloc[i].收盘 * self.trade_amount ) :
	# 				self.account.trade_update(
	# 					self.data.iloc[i].日期,
	# 					'B',
	# 					self.symbol,
	# 					self.trade_amount,
	# 					self.data.iloc[i].收盘
	# 					)
	# 			# 当日收盘价上穿upper，且有持仓时，以收盘价清仓
	# 			elif self.data.iloc[i].收盘 > self.data.iloc[i].upper and (
	# 				self.symbol in self.account.position['symbol'].values and self.account.position[self.account.position['symbol'] == self.symbol].iloc[-1].amount > 0) :
	# 				self.account.trade_update(
	# 					self.data.iloc[i].日期,
	# 					'S',
	# 					self.symbol,
	# 					self.account.position[self.account.position['symbol'] == self.symbol].iloc[-1].amount,
	# 					self.data.iloc[i].收盘
	# 					)
	# 			# 无买卖操作时，更新资产数据
	# 			else:
	# 				# date, symbol, price
	# 				self.account.no_trade_update_asset(self.data.iloc[i].日期, self.symbol, self.data.iloc[i].收盘)


	def by_boll(self):
		### 由下至上突破下轨，买入；由上之下跌破上轨，卖出
		for i in range(0, self.data.shape[0]):
			# 如果当天一字涨停或者跌停，无需交易
			if self.if_limit_move(self.data.iloc[i].最高, self.data.iloc[i].最低, self.data.iloc[i].涨跌幅):
				self.account.no_trade_update_asset(self.data.iloc[i].日期, self.symbol, self.data.iloc[i].收盘)
				continue

			# 布林带数据为空无需判断买卖时，只需更新资产数据;交易日第一天，无法判断上一天的股价和布林带之间的关系，无需判断买卖
			if pd.isnull(self.data.iloc[i]['ma20']) or i == 0:
				self.account.no_trade_update_asset(self.data.iloc[i].日期, self.symbol, self.data.iloc[i].收盘)
			else:
				# 买入条件：前一天收盘价低于下轨，且当日收盘价高于下轨，且现金足够
				if self.data.iloc[i].收盘 > self.data.iloc[i].lower and (self.data.iloc[i-1].收盘 <= self.data.iloc[i-1].lower) and (self.account.asset.iloc[-1].cash >= self.data.iloc[i].收盘 * self.trade_amount ) :
					self.account.trade_update(
						self.data.iloc[i].日期,
						'B',
						self.symbol,
						self.trade_amount,
						self.data.iloc[i].收盘
						)
				# 卖出条件：前一天收盘价高于上轨，且当日收盘价低于上轨，且有持仓
				elif self.data.iloc[i].收盘 < self.data.iloc[i].upper and self.data.iloc[i-1].收盘 >= self.data.iloc[i-1].upper and (
				self.symbol in self.account.position['symbol'].values 
				and self.account.position[self.account.position['symbol'] == self.symbol].iloc[-1].amount > 0) :
					self.account.trade_update(
						self.data.iloc[i].日期,
						'S',
						self.symbol,
						self.trade_amount,
						self.data.iloc[i].收盘
						)
				# 无买卖操作时，更新资产数据
				else:
					# date, symbol, price
					self.account.no_trade_update_asset(self.data.iloc[i].日期, self.symbol, self.data.iloc[i].收盘)

	def by_right_attack(self):
		"""右侧追击"""
		# 定义两个变量，分别存放前高以及追击完成后的最高股价
		last_higt = max_price = None
		for i in range(180, self.data.shape[0]):
			# 如果当天一字涨停或者跌停，无需交易
			if self.if_limit_move(self.data.iloc[i].最高, self.data.iloc[i].最低, self.data.iloc[i].涨跌幅):
				self.account.no_trade_update_asset(self.data.iloc[i].日期, self.symbol, self.data.iloc[i].收盘)
				continue

			# 更新前半年最高价
			last_higt = self.data['最高'][i-180:i].max()

			# 无持仓(持仓数据为空或者持仓数量为零)
			if self.account.position.empty or self.account.position.iloc[-1].amount == 0:
				# 价格未突破
				if self.data.iloc[i].收盘 <= last_higt:
					self.account.no_trade_update_asset(self.data.iloc[i].日期, self.symbol, self.data.iloc[i].收盘)
					continue
				# 破新高买入
				elif self.account.asset.iloc[-1].cash >= self.data.iloc[i].收盘 * self.trade_amount :
					self.account.trade_update(
						self.data.iloc[i].日期,
						'B',
						self.symbol,
						self.trade_amount,
						self.data.iloc[i].收盘
						)
			# 有持仓
			else:
				# 持仓小于400
				if self.account.position.iloc[-1].amount <= 400:
					# 跌破8%，止损
					if self.data.iloc[i].收盘 <= self.account.order.iloc[-1].trade_price * 0.92 :
						self.account.trade_update(
							self.data.iloc[i].日期,
							'S',
							self.symbol,
							self.account.position[self.account.position['symbol'] == self.symbol].iloc[-1].amount,
							self.data.iloc[i].收盘
							)
					# 上涨10%，追击
					elif self.data.iloc[i].收盘 >= self.account.order.iloc[-1].trade_price * 1.1 and (self.account.asset.iloc[-1].cash >= self.data.iloc[i].收盘 * self.trade_amount):
						self.account.trade_update(
							self.data.iloc[i].日期,
							'B',
							self.symbol,
							self.trade_amount,
							self.data.iloc[i].收盘
							)
				# 右侧追击完成，设止盈保护
				else:
					# 更新最高点（从最后一次买入后开始计算）
					max_price = self.account.order.iloc[-1].trade_price
					if self.data.iloc[i]['最高'] > self.account.order.iloc[-1].trade_price :
						max_price = self.data.iloc[i]['最高']
					# 最高点下跌8% 止盈
					if self.data.iloc[i]['收盘'] <= max_price * 0.92 :
						self.account.trade_update(
							self.data.iloc[i].日期,
							'S',
							self.symbol,
							self.account.position[self.account.position['symbol'] == self.symbol].iloc[-1].amount,
							self.data.iloc[i].收盘
							)


	def by_mean(self):
		pass


	def main(self):
		#选择交易策略
		if self.trade_strategy == 'boll' :
			self.by_boll()

		elif self.trade_strategy == 'right_attack':
			self.by_right_attack()

		elif self.trade_strategy == 'mean' :
			self.by_mean()
		else :
			pass


if __name__ == '__main__':
	dfcf_df = ak.stock_zh_a_hist(symbol='300059', period="daily", start_date="20011101", end_date='20221231', adjust="qfq")
	trade = Trade('300059', dfcf_df, 'right_attack')
	trade.main()
	print(trade.account.order)


