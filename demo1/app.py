import os
import secrets
from flask import Flask, flash, render_template, render_template_string, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote_plus
from flask import jsonify
from sqlalchemy import text 

UPLOAD_FOLDER = 'static/images/recipeimages'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Encode the special characters in the password
password = 'Venkat@1211'
encoded_password = quote_plus(password)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:{encoded_password}@localhost/savorysync'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Add email field
    password = db.Column(db.String(512), nullable=False)
   

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

class Recipe(db.Model):
    __tablename__ = 'recipe'
    recipe_number = db.Column(db.Integer, primary_key=True)
    recipe_type = db.Column(db.String(255), nullable=False)
    recipe_image = db.Column(db.String(255), nullable=False)
    recipe_name = db.Column(db.String(100), nullable=False)
    recipe_ingredients = db.Column(db.Text, nullable=False)
    recipe_details = db.Column(db.Text, nullable=False)




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('User already registered. Please login.', 'signup_error')
        return redirect(url_for('index'))

    hashed_password = generate_password_hash(password)

    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    flash('Successfully registered! You can now log in.', 'signup_success')

    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
@app.route('/login', methods=['POST'])
def login():
    username_or_email = request.form['username']
    password = request.form['password']

    # Adjust query to consider username or email
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if user:
        # User exists, check password
        if check_password_hash(user.password, password):
            session['username'] = user.username

            # Passwords match, allow login
            flash('Successfully logged in!', 'login_success')
            # Use the 'redirect' function to go to the dashboard route
            return redirect(url_for('dashboard'))
        else:
            # Invalid password
            flash('Invalid password. Please try again.', 'login_error')
    else:
        # User does not exist
        flash('User not registered. Please sign up.', 'login_error')

    # If login fails, redirect back to the index (login) page
    return redirect(url_for('index'))
    

@app.route('/dashboard')        
def dashboard():
    username = session.get('username', 'Guest')

    # Pass the username to the dashboard template
    return render_template('dashboard.html', username=username)


@app.route('/recipe_search', methods=['GET', 'POST'])
def recipe_search():
    # Get user inputs from the form
    recipe_type = request.args.get('type')
    recipe_number_str = request.args.get('number')

    # Validate inputs
    if recipe_type not in ['veg', 'nonveg'] or not recipe_number_str or not recipe_number_str.isdigit():
        flash('Invalid inputs. Please select a valid type and number of recipes.', 'error')
        return render_template('recipe_search.html', recipes=[])

    recipe_number = int(recipe_number_str)

    # Query the database for recipes based on user input
    query = text(f"SELECT * FROM recipe WHERE recipe_type = :recipe_type LIMIT :recipe_number")
    recipes = db.session.execute(query, {'recipe_type': recipe_type, 'recipe_number': recipe_number})

    # Fetch all rows from the ResultProxy
    recipe_rows = recipes.fetchall()

    # Check if recipes were found
    if recipe_rows:
        # Prepare a list to hold dictionaries of recipe details
        recipe_list = []
        for recipe in recipe_rows:
            recipe_dict = {
                'recipe_number': recipe.recipe_number,
                'recipe_name': recipe.recipe_name,
                'recipe_image': recipe.recipe_image,
            }
            recipe_list.append(recipe_dict)

        # Render the template with the obtained recipes
        return render_template('recipe_search.html', recipes=recipe_list)
    else:
        # No recipes found
        flash('No recipes found.', 'recipe_search_info')
        return render_template('recipe_search.html', recipes=[])


# Add this route to handle the case where the 'number' parameter is missing
@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400

@app.route('/recipe/<int:recipe_number>')
def view_recipe_details(recipe_number):
    # Query the database to get details of the selected recipe
    recipe = Recipe.query.filter_by(recipe_number=recipe_number).first()

    if recipe:
        return render_template('recipe_show.html', recipe=recipe)
    else:
        flash('Recipe not found.', 'error')
        return redirect(url_for('index'))

def generate_unique_filename(recipe_number, filename):
    _, ext = os.path.splitext(filename)
    return f"recipe{recipe_number}{ext}"

def update_recipe_image_name(recipe_number, new_filename):
    recipe = Recipe.query.filter_by(recipe_number=recipe_number).first()
    if recipe:
        recipe.recipe_image = new_filename
        db.session.commit()
    else:
        # Handle the case where the recipe with the given recipe number is not found
        flash('Recipe not found', 'error')

def get_next_recipe_number():
    last_recipe = Recipe.query.order_by(Recipe.recipe_number.desc()).first()
    if last_recipe:
        return last_recipe.recipe_number + 1
    else:
        return 1  # Assuming the first recipe starts with number 1

success_message = """
<h2>Recipe added successfully!</h2>
<p>Please visit the <a href="{{ url_for('recipe_search') }}">recipes page</a> for your recipes.</p>
<p>If you want to add more recipes, kindly refresh the page.</p>
"""

@app.route('/add_recipes', methods=['GET', 'POST'])
def add_recipes():
    if request.method == 'POST':
        # Handle POST request to add recipes
        recipe_type = request.form['recipeType']
        recipe_name = request.form['recipeName']
        recipe_ingredients = request.form['recipeIngredients']
        recipe_details = request.form['recipeDetails']

        # Check if the post request has the file part
        if 'recipeImage' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        recipe_image = request.files['recipeImage']

        # If the user does not select a file, the browser submits an empty part without a filename
        if recipe_image.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if recipe_image:
            # Generate a unique filename
            new_filename = generate_unique_filename(get_next_recipe_number(), recipe_image.filename)

            # Save the uploaded image to the correct directory using absolute path
            upload_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            recipe_image.save(os.path.join(upload_path, new_filename))

            # Update the recipe image name in the database
            recipe = Recipe(
                recipe_type=recipe_type,
                recipe_image=new_filename,
                recipe_name=recipe_name,
                recipe_ingredients=recipe_ingredients,
                recipe_details=recipe_details
            )
            db.session.add(recipe)
            db.session.commit()

            flash('Recipe added successfully!', 'success')

            # Render the success message template
            return render_template_string(success_message)

        else:
            flash('Failed to add recipe', 'error')
            return redirect(url_for('add_recipes'))

    else:
        # Handle GET request to render the add recipes form
        return render_template('add_recipes.html')


@app.route('/to_do_list_recipe')
def to_do_list_recipe():
    # Add logic for to-do list recipe
    return render_template('To_do_list_recipe.html')  # Create to_do_list_recipe.html template

@app.route('/about')
def about():
    # Add logic for the about section
    return render_template('about.html')  # Create about.html template

@app.route('/logout')
def logout():
    # Add logic for logout
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
