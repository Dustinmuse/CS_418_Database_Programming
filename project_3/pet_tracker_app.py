from pymongo import MongoClient

def create_pet_tracker_db():
    # Connect to MongoDB server
    client = MongoClient("mongodb://localhost:27017/")
    
    # Create the "Pet Tracker" database
    db = client["Pet_Tracker"]
    
    # Create collections
    owners_collection = db["Owners"]
    pets_collection = db["Pets"]
    activities_collection = db["Activities"]
    
    print("Database and collections created successfully!")
    return db


def add_owner(db, first_name, last_name, email, phone, dob, address):
    owners_collection = db["Owners"]
    owner_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "date_of_birth": dob,
        "address": address
    }
    result = owners_collection.insert_one(owner_data)
    print(f"Owner added with ID: {result.inserted_id}")
    return result.inserted_id


def register_pet(db, owner_id, pet_name, pet_type, breed, age, weight, vaccination_status, adoption_date, favorite_foods):
    pets_collection = db["Pets"]
    pet_data = {
        "owner_id": owner_id,
        "name": pet_name,
        "type": pet_type,
        "breed": breed,
        "age": age,
        "weight": weight,
        "vaccination_status": vaccination_status,
        "adoption_date": adoption_date,
        "favorite_foods": favorite_foods
    }
    result = pets_collection.insert_one(pet_data)
    print(f"Pet registered with ID: {result.inserted_id}")
    return result.inserted_id


def update_pet_info(db, pet_id, updates):
    pets_collection = db["Pets"]
    result = pets_collection.update_one({"_id": pet_id}, {"$set": updates})
    if result.modified_count > 0:
        print(f"Pet with ID {pet_id} updated successfully.")
    else:
        print(f"No updates made for pet with ID {pet_id}.")


def log_activity(db, pet_id, activity_type, duration, date, location, notes):
    activities_collection = db["Activities"]
    activity_data = {
        "pet_id": pet_id,
        "activity_type": activity_type,
        "duration": duration,
        "date": date,
        "location": location,
        "notes": notes
    }
    result = activities_collection.insert_one(activity_data)
    print(f"Activity logged with ID: {result.inserted_id}")
    return result.inserted_id


def get_activities(db, pet_id, activity_type=None):
    activities_collection = db["Activities"]
    query = {"pet_id": pet_id}
    if activity_type:
        query["activity_type"] = activity_type
    activities = activities_collection.find(query).sort("date", -1)
    return list(activities)


def get_total_time_per_activity(db, pet_id):
    activities_collection = db["Activities"]
    pipeline = [
        {"$match": {"pet_id": pet_id}},
        {"$group": {"_id": "$activity_type", "total_time": {"$sum": "$duration"}}}
    ]
    results = activities_collection.aggregate(pipeline)
    return list(results)


def get_most_frequent_activity(db, pet_id):
    activities_collection = db["Activities"]
    pipeline = [
        {"$match": {"pet_id": pet_id}},
        {"$group": {"_id": "$activity_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    result = list(activities_collection.aggregate(pipeline))
    return result[0] if result else None

def main():
    # Call the function to create the database and collections
    db = create_pet_tracker_db()

    while True:
        print("\nPet Tracker Menu:")
        print("1. Add Owner")
        print("2. Register Pet")
        print("3. Log Activity")
        print("4. View Activities")
        print("5. View Total Time Per Activity")
        print("6. View Most Frequent Activity")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            first_name = input("Enter first name: ")
            last_name = input("Enter last name: ")
            email = input("Enter email: ")
            phone = input("Enter phone: ")
            dob = input("Enter date of birth (YYYY-MM-DD): ")
            address = input("Enter address: ")
            add_owner(db, first_name, last_name, email, phone, dob, address)

        elif choice == "2":
            owner_id = input("Enter owner ID: ")
            pet_name = input("Enter pet name: ")
            pet_type = input("Enter pet type: ")
            breed = input("Enter breed: ")
            age = int(input("Enter age: "))
            weight = float(input("Enter weight: "))
            vaccination_status = input("Enter vaccination status: ")
            adoption_date = input("Enter adoption date (YYYY-MM-DD): ")
            favorite_foods = input("Enter favorite foods (comma-separated): ").split(",")
            register_pet(db, owner_id, pet_name, pet_type, breed, age, weight, vaccination_status, adoption_date, favorite_foods)

        elif choice == "3":
            pet_id = input("Enter pet ID: ")
            activity_type = input("Enter activity type: ")
            duration = int(input("Enter duration (in minutes): "))
            date = input("Enter date (YYYY-MM-DD): ")
            location = input("Enter location: ")
            notes = input("Enter notes: ")
            log_activity(db, pet_id, activity_type, duration, date, location, notes)

        elif choice == "4":
            pet_id = input("Enter pet ID: ")
            activity_type = input("Enter activity type (optional, press Enter to skip): ")
            activities = get_activities(db, pet_id, activity_type if activity_type else None)
            print("Activities:", activities)

        elif choice == "5":
            pet_id = input("Enter pet ID: ")
            total_time = get_total_time_per_activity(db, pet_id)
            print("Total time per activity:", total_time)

        elif choice == "6":
            pet_id = input("Enter pet ID: ")
            most_frequent = get_most_frequent_activity(db, pet_id)
            print("Most frequent activity:", most_frequent)

        elif choice == "7":
            print("Exiting Pet Tracker. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()