from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

API_KEY = "TopSecretAPIKey"

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}



with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record

@app.route("/random")
def get_random_cafe():
    random_cafe = random.choice(Cafe.query.all())

    return jsonify(
        cafe= random_cafe.to_dict()
    )

@app.route("/all")
def get_all_cafe():
    all_cafes = Cafe.query.all()

    return jsonify( cafes = [cafe.to_dict() for cafe in all_cafes] )

# @app.route("/all")
# def get_all_cafes():
#     result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
#     all_cafes = result.scalars().all()
    
#     return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route("/search")
def search_cafe():
    query_location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    # Note, this may get more than one cafe per location
    cafes_in_location = result.scalars().all()
    if cafes_in_location:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes_in_location])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


@app.route("/add", methods=["POST"])
def post_new_cafe():
    try:
        new_cafe = Cafe(
            name=request.form['name'],
            location=request.form['location'],
            seats=request.form['seats'],
            img_url=request.form['img_url'],
            map_url=request.form['map_url'],
            coffee_price=request.form['coffee_price'],
            has_wifi=bool(request.form['has_wifi']),
            has_toilet=bool(request.form['has_toilet']),
            has_sockets=bool(request.form['has_sockets']),
            can_take_calls=bool(request.form['can_take_calls']),
        )
    except KeyError:
        return jsonify(error={"Bad Request": "Some or all fields were incorrect or missing."})
    else:
        with app.app_context():
            db.session.add(new_cafe)
            db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})

@app.route("/update-price/<int:cafe_id>", methods=["PATCH", "GET"])
def update_price(cafe_id):
    new_price = float(request.args.get("new_price"))
    formatted_price = str("{:.2f}".format(new_price))

    cafe_to_update = db.session.get(Cafe, cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = f"£{formatted_price}"
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Bad Request": "The cafe's id is invalid."}), 404

@app.route("/report-closed/<int:cafe_id>")
def delete_cafe(cafe_id):
    key = request.args.get("api-key")
    if key != API_KEY:
        return jsonify(error={"Error": "Sorry, that's not allowed, make sure that you have the correct api key."}), 403
    else:
        cafe_to_delete = db.session.get(Cafe, cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe."}), 200
        else:
            return jsonify(error={"Bad Request": "The cafe's id is invalid."}), 404
        
if __name__ == '__main__':
    app.run(debug=True)
