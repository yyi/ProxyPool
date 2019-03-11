#!/usr//local/bin/python3
__doc__ = '''
数据表生成脚本
用户从特定的 Excel 文件中逐个获得每个表的定义信息，从而生成符合 Hive 要求的分区表
Excel 中表的定义如下：

'''
__author__ = 'wgzhao<wgzhao@gmail.com>'

import pandas as pd
import pinyin
def type_convert(s):
    '''
    转换 Excel 文档中对字段类型定义的转换
    转换规则为：
    C(x) -> String
    V(x) -> String
    N(x,y) -> DECIMAL(x,y)
    '''
    if s[0].upper() in ['C','V']:
        return 'STRING'
    elif s[0].upper() in ['N']:
        return 'DECIMAL' + s[1:]
def c2p(c):
    '''获得中文名字的拼音首字母'''
    py = pinyin.get(c, delimiter='|', format='strip')
    return ''.join([x[0] for x in py.split('|')])

def generate_table(df, tblname):
    '''
    从 Excel 中获得表的字段描述、字段名称以及字段类型定义信息
    生成符合 Hive 规范的分区表
    表名的定义为 z_<表定义中文拼音首字母>[n]
    如遇到相同名称，则增加数字前缀，前缀从2开始
    '''
    tbl_english_name = 'z_' + c2p(tblname.split('-')[-1])
    tbl_sql = 'create table infadb.{} (\n'.format(tbl_english_name)
    for _, item in df[['字段描述','源英文字段名','数据类型']].dropna().iterrows():
        tbl_sql += "{} {} COMMENT '{}',\n".format(item[1],type_convert(item[2]), item[0])
    tbl_sql = tbl_sql[:-2] + ") COMMENT '{}' \n partitioned by (logdate STRING); \n".format(tblname)
    return tbl_sql

fd = pd.read_excel('F:\\tsm\\方正\\资管报送\\资管新规接口规范(2).xlsx', sheet_name=None)

all_sqls = ''
sheets = list(fd.keys())
for sheet in sheets[6:]:
    all_sqls  += generate_table(fd[sheet], sheet) + '\n'
open('schemas.sql','w').write(all_sqls)

# 获得 Excel 表格与实际数据表对应关系
# sheets = list(fd.keys())
# print("""
# | 表格名称     | 表名称(hive) |
# |-------------|-------------|
# """)
# for item in sheets[6:]:
#     tbl_english_name = 'infadb.z_' + c2p(item.split('-')[-1])
#     print("| {} | {} |".format(item, tbl_english_name))