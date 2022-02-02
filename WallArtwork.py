from PIL import Image
from urllib import parse, request
import requests, json


def choice(question, list_answers):
    """
    Simple function to help to ask questions.

        Parameters:
                question (str): question to ask to the user,
                list_answers (list): answers.

        Return:
                (str): number return the response.
    """
    choices = []
    print(f"\n{question}?\n")
    for i in range(len(list_answers)):
        print(f"[{i+1}] - {list_answers[i]}")
        choices.append(str(i + 1))
    print("[q] - Go back")
    reponse = input("\n➔ ")
    if reponse == "q":
        return None
    if reponse not in choices or reponse == "":
        print(f"\n⚠ Error : Please select a number between {choices[0]} and {choices[-1]} !")
        return choice(question, list_answers)
    else:
        return int(reponse) - 1


def search_artist(artist):
    """
    Function to search an artist using iTunes API.

        Parameters:
                artist (str): name of the artist to search

        Return:
                (str): artistID of the searched artist
    """
    try:
        artists = requests.get(
            f"https://itunes.apple.com/search?term={parse.quote(artist)}&entity=musicArtist&limit=10", timeout=3
        )
        if artists.status_code != 200:
            raise (ConnectionError())
    except:
        print("\n\n⚠ Error : Please make sure you're connected to internet")
        artist = input("\nWhat is the artist's name?\n➔ ")
        return search_artist(artist)
    artists = json.loads(artists.text)
    choices = []
    if artists["resultCount"] == 0:
        print(f"\n\n⚠ Error : Please enter a valid artist !")
        artist = input("\nWhat is the artist's name?\n➔ ")
        return search_artist(artist)
    if artists["resultCount"] == 1:
        return artists["results"][0]["artistId"]
    else:
        for i in range(artists["resultCount"]):
            if "primaryGenreName" not in artists["results"][i]:
                artists["results"][i]["primaryGenreName"] = "Unknown genre"
            choices.append(
                f"{artists['results'][i]['artistName']} - {artists['results'][i]['primaryGenreName']} ({artists['results'][i]['artistLinkUrl']})"
            )
        artist = choice("Which artist do you want to choose", choices)
        if artist == None:
            artist = input("\nWhat is the artist's name?\n➔ ")
            return search_artist(artist)
        return artists["results"][artist]["artistId"]


def search_album(id_artist):
    """
    Function to search the artwork of an album using iTunes API and the id of an artist.

        Parameters:
                id_artist (str): id of the artist to search

        Return:
                (str): artwork (1000x1000) of the searched album
    """
    try:
        albums = requests.get(f"https://itunes.apple.com/lookup?id={id_artist}&entity=album&limit=30", timeout=3)
        if albums.status_code != 200:
            raise (ConnectionError())
    except:
        print("\n\n⚠ Error : Please make sure you're connected to internet")
        artist = input("\nWhat is the artist's name?\n➔ ")
        return search_album(search_artist(artist))
    albums = json.loads(albums.text)
    choices = []
    if albums["resultCount"] == 0:
        print(f"\n\n⚠ Error : Please enter a valid artist !")
        artist = input("\nWhat is the artist's name ?\n➔ ")
        return search_album(search_artist(artist))
    for i in range(albums["resultCount"] - 1):
        choices.append(f"{albums['results'][i+1]['collectionName']}")
    album = choice("Which album do you want to choose", choices)
    if album == None:
        artist = input("\nWhat is the artist's name?\n➔ ")
        return search_album(search_artist(artist))
    return albums["results"][album + 1]["artworkUrl100"].replace("100x100", "600x600")


def generate(artwork):
    """
    Function to generate the picture containing 18 artworks.

        Parameters:
                artwork (list): URLs of the artworks to search (needs to be 18)
    """
    l, w = 120, 0
    img = Image.new(mode="RGB", size=(2160, 4296), color=(0, 0, 0))
    print("Downloading album covers...")
    for i in range(18):
        try:
            request.urlretrieve(artwork[i], "background.png")
        except:
            print("\n\n⚠ Error : Please make sure you're connected to internet")
            q = ""
            while q != "y" and q != "n":
                q = input("\n\nDo you want to retry?\n[y] - Yes\n[n] - No\n➔ ")
            if q == "y":
                return generate(artwork)
            else:
                return ()
        img1 = Image.open("background.png")
        img1 = img1.resize((720, 720))
        img.paste(img1, (w, l))
        l += 720
        if i == 5:
            l, w = 150, 720
        elif i == 11:
            l, w = 0, 1440
    print("Saving the image...")
    img = img.crop((0, 200, 2160, 4296))
    img.save("background.png")
    print("Image saved!")


artwork = []
for i in range(18):
    artist = input(f"\nWhat is the artist's name? ({i+1}/18)\n➔ ")
    artwork.append(search_album(search_artist(artist)))
generate(artwork)
