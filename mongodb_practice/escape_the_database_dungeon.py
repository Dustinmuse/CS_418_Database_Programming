import pymongo

def populate_data(mycol):
  data = [
    {

      "room_id": 1,

      "description": "You are in a dimly lit room with a locked door and a dusty old rug.",

      "clue": "Lift the rug to find the key.",

      "item": "key",

      "status": "locked",

      "next_room": 2

    },

    {

      "room_id": 2,

      "description": "The room is brighter, with a chest in the center and strange markings on the walls.",

      "clue": "Use the key to unlock the chest and find the code.",

      "item": "code",

      "status": "locked",

      "next_room": 3

    },

    {

      "room_id": 3,

      "description": "This room has a glowing orb floating mid-air. The orb whispers a question: 'What is 5 + 7?'",

      "clue": "Solve the riddle to reveal the next path.",

      "item": "answer_12",

      "status": "locked",

      "next_room": 4

    },

    {

      "room_id": 4,

      "description": "A dark room with flickering lights. A console blinks with the words 'Enter the magic word.'",

      "clue": "The word is hidden in the orb's glow.",

      "item": "magic_word",

      "status": "locked",

      "next_room": 5

    },

    {

      "room_id": 5,

      "description": "You are in a library filled with ancient books. One book is glowing faintly.",

      "clue": "Find the glowing book and open it to retrieve a map.",

      "item": "map",

      "status": "locked",

      "next_room": 6

    },

    {

      "room_id": 6,

      "description": "A hallway with strange symbols on the walls. The map reveals the correct path.",

      "clue": "Use the map to decipher the symbols.",

      "item": "path_code",

      "status": "locked",

      "next_room": 7

    },

    {

      "room_id": 7,

      "description": "A room with a pedestal. A glowing scroll lies on top of it.",

      "clue": "Read the scroll to reveal the final instructions.",

      "item": "final_instructions",

      "status": "locked",

      "next_room": 8

    },

    {

      "room_id": 8,

      "description": "The final room! A glowing portal stands before you, ready to take you out.",

      "clue": "Enter the portal and escape!",

      "item": None,

      "status": "unlocked",

      "next_room": None

    }
  ]

  mycol.insert_many(data)

def dungeon_escape(mycol):
  room_number = 1

  match room_number:
    case 1:
      for room_info in mycol.find({"room_id": 1}, {"_id": 0, "description": 1, "clue": 1}):
        print(room_info)
        if room_info["item"] is not None:
          print(f"you have gained an item: {room_info["item"]}")
        else:
          print("there was no item for you in this room")
        while room_info["status"] == "locked":
          answer = input("Did you solve it: (yes/no)")
          if answer == "yes":
            print(f"you solved the riddle and enter the next room: room {room_info["next_room"]}")
            update_query = {"room_id": 1}
            new_value = {"$set": {"status": "unlocked"}}
            mycol.update_one(update_query, new_value)
          else:
            print("you need to solve it to continue to the next room")
        room_number = room_info["next_room"]
    case 2:
      for room_info in mycol.find({"room_id": 2}, {"_id": 0, "description": 1, "clue": 1}):
        print(room_info)
        if room_info["item"] is not None:
          print(f"you have gained an item: {room_info["item"]}")
        else:
          print("there was no item for you in this room")
        while room_info["status"] == "locked":
          answer = input("Did you solve it: (yes/no)")
          if answer == "yes":
            print(f"you solved the riddle and enter the next room: room {room_info["next_room"]}")
            update_query = {"room_id": 2}
            new_value = {"$set": {"status": "unlocked"}}
            mycol.update_one(update_query, new_value)
          else:
            print("you need to solve it to continue to the next room")
        room_number += 1
    case 3:
      for room_info in mycol.find({"room_id": 3}, {"_id": 0, "description": 1, "clue": 1}):
        print(room_info)
        if room_info["item"] is not None:
          print(f"you have gained an item: {room_info["item"]}")
        else:
          print("there was no item for you in this room")
        while room_info["status"] == "locked":
          answer = input("Did you solve it: (yes/no)")
          if answer == "yes":
            print(f"you solved the riddle and enter the next room: room {room_info["next_room"]}")
            update_query = {"room_id": 3}
            new_value = {"$set": {"status": "unlocked"}}
            mycol.update_one(update_query, new_value)
          else:
            print("you need to solve it to continue to the next room")
        room_number += 1
    case 4:
      for room_info in mycol.find({"room_id": 4}, {"_id": 0, "description": 1, "clue": 1}):
        print(room_info)
        if room_info["item"] is not None:
          print(f"you have gained an item: {room_info["item"]}")
        else:
          print("there was no item for you in this room")
        while room_info["status"] == "locked":
          answer = input("Did you solve it: (yes/no)")
          if answer == "yes":
            print(f"you solved the riddle and enter the next room: room {room_info["next_room"]}")
            update_query = {"room_id": 4}
            new_value = {"$set": {"status": "unlocked"}}
            mycol.update_one(update_query, new_value)
          else:
            print("you need to solve it to continue to the next room")
        room_number += 1
    case 5:
      for room_info in mycol.find({"room_id": 5}, {"_id": 0, "description": 1, "clue": 1}):
        print(room_info)
        if room_info["item"] is not None:
          print(f"you have gained an item: {room_info["item"]}")
        else:
          print("there was no item for you in this room")
        while room_info["status"] == "locked":
          answer = input("Did you solve it: (yes/no)")
          if answer == "yes":
            print(f"you solved the riddle and enter the next room: room {room_info["next_room"]}")
            update_query = {"room_id": 5}
            new_value = {"$set": {"status": "unlocked"}}
            mycol.update_one(update_query, new_value)
          else:
            print("you need to solve it to continue to the next room")
        room_number += 1
    case 6:
      for room_info in mycol.find({"room_id": 6}, {"_id": 0, "description": 1, "clue": 1}):
        print(room_info)
        if room_info["item"] is not None:
          print(f"you have gained an item: {room_info["item"]}")
        else:
          print("there was no item for you in this room")
        while room_info["status"] == "locked":
          answer = input("Did you solve it: (yes/no)")
          if answer == "yes":
            print(f"you solved the riddle and enter the next room: room {room_info["next_room"]}")
            update_query = {"room_id": 6}
            new_value = {"$set": {"status": "unlocked"}}
            mycol.update_one(update_query, new_value)
          else:
            print("you need to solve it to continue to the next room")
        room_number += 1
    case 7:
      for room_info in mycol.find({"room_id": 7}, {"_id": 0, "description": 1, "clue": 1}):
        print(room_info)
        if room_info["item"] is not None:
          print(f"you have gained an item: {room_info["item"]}")
        else:
          print("there was no item for you in this room")
        while room_info["status"] == "locked":
          answer = input("Did you solve it: (yes/no)")
          if answer == "yes":
            print(f"you solved the riddle and enter the next room: room {room_info["next_room"]}")
            update_query = {"room_id": 7}
            new_value = {"$set": {"status": "unlocked"}}
            mycol.update_one(update_query, new_value)
          else:
            print("you need to solve it to continue to the next room")
        room_number += 1
    case 8:
      for room_info in mycol.find({"room_id": 8}, {"_id": 0, "description": 1, "clue": 1}):
        print(room_info)
        if room_info["item"] is not None:
          print(f"you have gained an item: {room_info["item"]}")
        else:
          print("there was no item for you in this room")
        while room_info["status"] == "locked":
          answer = input("Did you solve it: (yes/no)")
          if answer == "yes":
            print(f"you solved the riddle and enter the next room: room {room_info["next_room"]}")
            update_query = {"room_id": 8}
            new_value = {"$set": {"status": "unlocked"}}
            mycol.update_one(update_query, new_value)
          else:
            print("you need to solve it to continue to the next room")
        room_number += 1

def reset_data(mycol):
  increment = 1
  while increment <= 7:
    update_query = {"room_id": increment}
    new_value = {"$set": {"status": "locked"}}
    mycol.update_one(update_query, new_value)
    increment += 1

def main():
  # Connects to mongodb and makes a database called dungeon and a collection called rooms
  client = pymongo.MongoClient()
  mydb = client["dungeon"]
  mycol = mydb["rooms"]

  # Populating the data into the above collection
  #populate_data(mycol)

  # Running the game
  dungeon_escape(mycol)

  # Resets the game data so it can be played again
  reset_data(mycol)

if __name__ == "__main__":
  main()