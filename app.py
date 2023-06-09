from flask import Flask, request, jsonify
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS
import json

from flask import send_file
import io
import csv
import pandas as pd




from datetime import datetime, timedelta

import copy

import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
CORS(app)

Base = sqlalchemy.orm.declarative_base()

engine = create_engine('sqlite:///admin.db', echo=True)
Session = sessionmaker(bind=engine)

# Create an engine for database2
engine2 = create_engine('sqlite:///exit_survey.db')
Session2 = sessionmaker(bind=engine2)

# Create an engine for database2
engine3 = create_engine('sqlite:///products.db')
Session3 = sessionmaker(bind=engine3)





class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)

class ExitSurvey(Base):
    __tablename__ = 'exit_survey'

    id = Column(Integer, primary_key=True, autoincrement=True)
    stars = Column(Integer, nullable=False)
    initiative = Column(String, nullable=False)
    further_improvement = Column(String, nullable=False)
    feedback = Column(String)

class ProductsFeedback(Base):
    __tablename__ = 'products_feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=False)
    product_category = Column(String, nullable=False)
    product_name = Column(String, nullable=False, unique=False)
    what_do_you_like_best = Column(String, nullable=False)
    unique = Column(String, nullable=False)



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    print(username, password)

    try:
        session = Session()
        user = session.query(User).filter_by(username=username).first()
        if user and user.password == password:
            print("Login successful")
            return jsonify({'success': True, 'status': 200})
        else:
            return jsonify({'success': False, 'message': 'Incorrect username or password'})
    except Exception as e:
        # Handle the exception here, for example, log it and return an error message
        print(f"An error occurred: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})
    finally:
        session.close()
    

# Database end

@app.route('/exit_survey', methods=['GET'])
def get_exit_survey():
    try:
        session2 = Session2()
        data = session2.query(ExitSurvey).all()

        # create a csv string from the data
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'stars', 'initiative', 'further_improvement', 'feedback'])
        for row in data:
            writer.writerow([row.id, row.stars, row.initiative, row.further_improvement, row.feedback])
        output.seek(0)

        # send the file as a response
        return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name='exit_survey.csv',
                         etag=False)
    
    except Exception as e:
        # Handle the exception here, for example, log it and return an error message
        print(f"An error occurred: {e}")
        return jsonify({'success': False, 'message': e})
    finally:
        session2.close()


@app.route('/exit_survey', methods=['POST'])
def post_exit_survey():
    try:

        Base.metadata.create_all(engine2)  # Create the table if it doesn't exist

        data = request.json
        session2 = Session2()
        exit_survey = ExitSurvey(stars=data['stars'], initiative=data['initiative'], further_improvement=data['further_improvement'], feedback=data['feedback'])
        session2.add(exit_survey)
        session2.commit()
        print("Exit survey added successfully")   
        return jsonify({'message': 'Exit survey added successfully.'}), 201
    except Exception as e:
        print(e)   
        return jsonify({'message': 'Error: ' + str(e)}), 500
    finally:
        session2.close()

# Database end

@app.route('/post_selection_post', methods=['POST'])
def post_selection_post():

    data = request.get_json()

    print("data", data)

    try:

        Base.metadata.create_all(engine3)  # Create the table if it doesn't exist
        session3 = Session3()
        
        name = data['name']
        product_category = data['product_category']
        product_name = data['product_name']
        what_do_you_like_best = data['what_do_you_like_best']
        unique = data['unique']

        new_feedback = ProductsFeedback(
            name=name,
            product_category=product_category,
            product_name=product_name,
            what_do_you_like_best=what_do_you_like_best,
            unique=unique
        )

        session3.add(new_feedback)
        session3.commit()
        session3.close()
        return {"message": "Feedback updated successfully."}, 200

    except Exception as e:
        # Catch any exceptions and return an error message
        print(e)
        return {"error": str(e)}, 500


@app.route('/post_selection_get', methods=['GET'])
def post_selection_get():

    try:
        session3 = Session3()

        # Query the database for all product feedbacks
        product_feedbacks = session3.query(ProductsFeedback).all()

        # Create a dictionary to store the unique counts for each product
        unique_counts = {}

        # Loop through each product feedback and count the number of occurrences of each unique value
        for feedback in product_feedbacks:
            category = feedback.product_category
            product = feedback.product_name
            unique_value = feedback.unique

            # If this is the first feedback for this category, initialize the counts dictionary for this category
            if category not in unique_counts:
                unique_counts[category] = {}

            # If this is the first feedback for this product in this category, initialize the counts dictionary for this product
            if product not in unique_counts[category]:
                unique_counts[category][product] = {"Very common": 0, "Differentiated": 0, "Super unique": 0}

            # Increment the count for this unique value for this product in this category
            if unique_value == "Very common":
                unique_counts[category][product]["Very common"] += 1
            elif unique_value == "Differentiated":
                unique_counts[category][product]["Differentiated"] += 1
            elif unique_value == "Super unique":
                unique_counts[category][product]["Super unique"] += 1

        session3.close()

        # Return the unique counts dictionary
        return json.dumps(unique_counts), 200
    
    except Exception as e:
        # Catch any exceptions and return an error message
        print(e)
        return {"error": str(e)}, 500


@app.route('/get_products_data', methods=['GET'])
def get_products_data():
    try:
        session3 = Session3()
        data = session3.query(ProductsFeedback).all()

        # create a csv string from the data
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'name', 'product_category', 'product_name', 'what_do_you_like_best', 'unique'])
        for row in data:
            writer.writerow([row.id, row.name, row.product_category, row.product_name, row.what_do_you_like_best, row.unique])
        output.seek(0)

        # send the file as a response
        return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name='products_data.csv',
                         etag=False)
    
    except Exception as e:
        # Handle the exception here, for example, log it and return an error message
        print(f"An error occurred: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'})
    finally:
        session3.close()

       


# @app.route('/post_selection_post', methods=['POST'])
# def post_selection_post():
#     try:
#         session3 = Session3()
#         data = session3.query(ProductsFeedback).all()

#         # create a csv string from the data
#         output = io.StringIO()
#         writer = csv.writer(output)
#         writer.writerow(['id', 'name', 'initiative', 'further_improvement', 'feedback'])
#         for row in data:
#             writer.writerow([row.id, row.name, row.initiative, row.further_improvement, row.feedback])
#         output.seek(0)

#         # send the file as a response
#         return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
#                          mimetype='text/csv',
#                          as_attachment=True,
#                          download_name='exit_survey.csv',
#                          etag=False)
    
#     except Exception as e:
#         # Handle the exception here, for example, log it and return an error message
#         print(f"An error occurred: {e}")
#         return jsonify({'success': False, 'message': 'An error occurred'})
#     finally:
#         session3.close()








