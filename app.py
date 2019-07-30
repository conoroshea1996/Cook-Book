from flask import Flask, render_template, request, url_for, redirect, session
import os
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt

from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'task_manager'
app.config["MONGO_URI"] = os.environ.get('MONGO_URI')
app.secret_key = 'secret_key'

mongo = PyMongo(app)

"""
HELPERS 
"""


def defaultImage(image):
    if image:
        return image
    else:
        return 'https://mamadips.com/wp-content/uploads/2016/11/defimage.gif'


@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        username = session['username']
    else:
        username = ''
    return render_template('index.html', user=username)


@app.route('/test')
def test():

    return render_template('test.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert(
                {'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'User name already exist'

    return render_template('register.html')


@app.route('/recipes')
def get_recipes():
    if 'username' in session:
        username = session['username']
    else:
        username = ''

    per_page = 6
    page = request.args.get(get_page_parameter(), type=int, default=1)
    recipes = mongo.db.Recipes.find()
    pagination = Pagination(page=page, total=recipes.count(), per_page=per_page,
                            search=False, record_name='recipes', css_framework='bootstrap4', alignment='center')

    recipe_page = recipes.skip((page - 1) * per_page).limit(per_page)

    return render_template('recipes.html', recipe=recipe_page, pagination=pagination, skill=mongo.db.skill.find(), orgin=mongo.db.cusine.find(), user=username)


@app.route('/add_recipe')
def add_recipe():
    return render_template('addrecipe.html', skill=mongo.db.skill.find(), orgin=mongo.db.cusine.find())


@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    tasks = mongo.db.Recipes
    tasks.insert_one({
        'name': request.form.get('name'),
        'skill': request.form.get('skill'),
        'cusine': request.form.get('cusine'),
        'recipe_des': request.form.get('recipe_des'),
        'image': defaultImage(request.form.get('image')),
        'ingredients': request.form.get('ingredients'),
        'instuctions': request.form.get('instuctions')
    })
    return redirect(url_for('get_recipes'))


@app.route('/single/<recipe_id>')
def recipe_info(recipe_id):
    recipe = mongo.db.Recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template('recipeInfo.html', recipeInfo=recipe)


@app.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
    mongo.db.Recipes.remove({'_id': ObjectId(recipe_id)})
    return redirect(url_for('get_recipes'))


@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    recipe = mongo.db.Recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template('editrecipe.html', recipeInfo=recipe, skill=mongo.db.skill.find(), orgin=mongo.db.cusine.find())


@app.route('/update_recipe/<recipe_id>', methods=['POST'])
def update_recipe(recipe_id):
    recipe = mongo.db.Recipes
    thisrecipe = mongo.db.Recipes.find_one({'_id': ObjectId(recipe_id)})

    def staySame(value, string):
        if value:
            return value
        else:
            return thisrecipe[string]

    recipe.update({'_id': ObjectId(recipe_id)}, {
        'name': staySame(request.form.get('name'), 'name'),
        'skill': request.form.get('skill'),
        'image': staySame(request.form.get('image'), 'image'),
        'cusine': request.form.get('cusine'),
        'ingredients': request.form.get('ingredients').strip(),
        'instuctions': request.form.get('instuctions').strip(),
    })
    return redirect(url_for('get_recipes'))


@app.route('/filter_recipes', methods=['GET', 'POST'])
def filter_recipes():
    recipe = mongo.db.Recipes
    skill = request.form.get('skill')
    if request.method == 'POST':
        recipes = recipe.find({'skill': skill})
        return render_template('filter.html', recipe=recipes)


@app.route('/pagination')
def pagination():
    if 'username' in session:
        username = session['username']
    else:
        username = ''

    per_page = 3
    page = request.args.get(get_page_parameter(), type=int, default=1)
    recipes = mongo.db.Recipes.find()
    pagination = Pagination(page=page, total=recipes.count(), per_page=per_page,
                            search=False, record_name='recipes', css_framework='bootstrap4', alignment='center')

    recipe_page = recipes.skip((page-1)*per_page).limit(per_page)

    return render_template('x.html',
                           users=recipe_page,
                           pagination=pagination,
                           user=username)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=os.environ.get('PORT'), debug=True)
