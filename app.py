#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import bottle
from bottle import get, post, run
from bottle import request, template, redirect
from bottle import HTTPError
from sqlalchemy import create_engine, Column, Integer, Unicode, DateTime, UnicodeText
from sqlalchemy.ext.declarative import declarative_base

from bottle.ext import sqlalchemy

from wtforms.form import Form
from wtforms import validators
from wtforms import StringField, IntegerField, TextAreaField

Base = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=True)

# bottle-sqlalchemyの設定
plugin = sqlalchemy.Plugin(
    engine,
    Base.metadata,
    keyword='db',  # 関数内で挿入される場合の変数名
    create=True,  # テーブルを作成するか
    commit=True,  # 関数終了時にコミットするか
    use_kwargs=False
)

# プラグインのインストール
bottle.install(plugin)


class Book(Base):
    # booksテーブル
    __tablename__ = 'books'

    # カラムの定義
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(100), nullable=False)
    author = Column(Unicode(100), nullable=False)
    price = Column(Integer, nullable=False)
    memo = Column(UnicodeText)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return "<Book('%s','%s', '%s', '%s', '%s')>" % (self.title, self.author, self.price, self.memo, self.created_at)


class BookForm(Form):
    title = StringField(u'タイトル', [
        validators.required(message=u"入力してください"),
        validators.length(min=1, max=100, message=u"100文字以下で入力してください")
    ])
    author = StringField(u'作者', [
        validators.required(message=u"入力してください"),
        validators.length(min=1, max=100, message=u"100文字以下で入力してください")
    ])
    price = IntegerField(u'価格', [
        validators.required(message=u"数値で入力してください")
    ])
    memo = TextAreaField(u'メモ', [
        validators.required(message=u"入力してください")
    ])


@get('/books')
def index(db):
    # booksテーブルから全件取得
    books = db.query(Book).all()

    # index.tplの描画
    return template('index', books=books, request=request)


@get('/books/add')
def new(db):
    form = BookForm()

    # add.tplの描画
    return template('edit', form=form, request=request)


@post('/books/add')
def create(db):
    form = BookForm(request.forms.decode())

    # フォームのバリデーション
    if form.validate():

        # Bookインスタンスの作成
        book = Book(
            title=form.title.data,
            author=form.author.data,
            price=form.price.data,
            memo=form.memo.data
        )

        # bookを保存
        db.add(book)

        # 一覧画面へリダイレクト
        redirect("/books")
    else:
        return template('edit', form=form, request=request)


@get('/books/<id:int>/edit')
def edit(db, id):
    # Bookの検索
    book = db.query(Book).get(id)

    # Bookが存在しない(404を表示）
    if not book:
        return HTTPError(404, 'Book is not found.')

    # フォームを作成
    form = BookForm(request.POST, book)

    # edit.tplを描画
    return template('edit', book=book, form=form, request=request)


@post('/books/<id:int>/edit')
def update(db, id):
    # Bookの検索
    book = db.query(Book).get(id)

    # Bookが存在しない(404を表示）
    if not book:
        return HTTPError(404, 'Book is not found.')

    form = BookForm(request.forms.decode())

    if form.validate():
        # book情報を更新
        book.title = form.title.data
        book.author = form.author.data
        book.price = form.price.data
        book.memo = form.memo.data

        # 一覧画面へリダイレクト
        redirect("/books")
    else:
        return template('edit', form=form, request=request)


@post('/books/<id:int>/delete')
def destroy(db, id):
    # Bookの検索
    book = db.query(Book).get(id)

    # Bookが存在しない(404を表示）
    if not book:
        return HTTPError(404, 'Book is not found.')

    # bookを削除
    db.delete(book)

    # 一覧画面へリダイレクト
    redirect("/books")


if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)



# 自分で書いたコード

# #!/usr/bin/env python 
# # -*- coding: utf-8 -*-

# #datetime
# from datetime import datetime

# # bottle関連
# import bottle
# from bottle import get, post, run
# from bottle import request, template, redirect
# from bottle import HTTPError

# # sqlalchemy関連
# from sqlalchemy import create_engine, Column, Integer, Unicode, DateTime, UnicodeText
# from sqlalchemy.ext.declarative import declarative_base

# # bottle-sqpalchemy
# from bottle.ext import sqlalchemy

# # wtforms関連
# from wtforms.form import Form
# from wtforms import validators
# from wtforms import StringField, IntegerField, TextAreaField

# Base = declarative_base()
# engine = create_engine('sqlite:///memory:', echo=True)


# # bottle-sqlalchemyの設定
# plugin = sqlalchemy.Plugin(
# 	engine,
# 	Base.metadata,
# 	keyword='db',	# 関数内で挿入される場合の変数名
# 	create=True,	# テーブルを作成するか
# 	commit=True,	# 関数終了時にトランザクションをコミットするか
# 	use_kwargs=False
# )

# # プラグインのインストール
# bottle.install(plugin)


# class Book(Base):

# 	# booksテーブルを使用
# 	__tablename__ = 'books'

# 	#カラムの定義
# 	id = Column(Integer, primary_key=True)
# 	title = Column(Unicode(100), nullable=False)
# 	price = Column(Integer, nullable=False)
# 	memo = Column(UnicodeText)
# 	created_at = Column(DateTime, default=datetime.now)

# 	def __repr__(self):
# 		return "<Book('%s', '%s', '%s', '%s', '%s')>" % (self.title, self.price, self.memo, self.created_at)


# class BookForm(Form):

# 	title = StringField(u'タイトル', [
# 		validators.required(message=u"入力してください"),
# 		validators.length(min=1, max=100, message=u"数値で入力してください")
# 	])

# 	price = IntegerField(u'価格', [
# 		validators.required(message=u"数値で入力してください")
# 	])

# 	memo = TextAreaField(u'メモ', [
# 		validators.required(message=u"入力してください")
# 	])


# @get('/books')
# def index(db):
	
# 	# booksテーブルから全件の取得
# 	books = db.query(Book).all()

# 	# index.tplの描画
# 	return template('index', books=books, request=request)


# @get('/book/add')
# def new(db):
	
# 	# BookFormインスタンスの作成
# 	form = BookForm()

# 	# edit.tplの描画
# 	return template('edit', form=form, request=request)


# @get('/books/<id:int>/edit')
# def edit(db, id):
	
# 	# Bookの検索
# 	book = db.query(Book).get(id)

# 	# Bookが存在しない(404を表示)
# 	if not book:
# 		return HTTPError(404, 'Book is not found.')

# 	# BookFormインスタンスの生成
# 	form = BookForm(request.POST, book)

# 	# edit.tplの描画
# 	return template('edit', book=book, form=form, request=request)


# @post('/books/add')
# def create(db):
# 	# 引数dbにsessionインスタンスが自動的に挿入される

# 	# BookFormインスタンスの生成
# 	form = BookForm(request.forms.decode())

# 	# フォームのバリデーション
# 	if form.validate():

# 		# Bookインスタンスの生成
# 		book = Book(
# 			title=form.title.data,
# 			price=form.price.data,
# 			memo=form.memo.data
# 		)

# 		# bookの保存
# 		db.add(book)

# 		# 一覧画面へリダイレクト
# 		redirect("/books")
# 	else:
# 		return template('edit', form=form, request=request)


# @post('/books/<id:int>/edit')
# def update(db, id):
	
# 	# Bookの検索
# 	book = db.query(Book).get(id)

# 	# Bookが存在しない(404を表示)
# 	if not book:
# 		return HTTPError(404, 'Book is not found.')

# 	# BookFormインスタンスの生成
# 	form = BookForm(request.forms.decode())

# 	# フォームのバリデーション
# 	if form.validate():

# 		# book情報の更新
# 		book.title = form.title.data
# 		book.price = form.price.data
# 		book.memo = form.memo.data

# 		# 一覧画面へのリダイレクト
# 		redirect("/books")
# 	else:
# 		return template('edit', form=form, request=request)


# @post('/books/<id:int>/delete')
# def destroy(db, id):
	
# 	# Bookの検索
# 	book = db.query.get(id)

# 	# Bookが存在しない(404を表示する)
# 	if not book:
# 		return HTTPError(404, 'Book is not found.')

# 	# bookの削除
# 	db.delete(book)

# 	# 一覧画面へリダイレクト
# 	redirect("/books")


# if __name__ == '__main__':
#     run(host='localhost', port=8080, debug=True, reloader=True)