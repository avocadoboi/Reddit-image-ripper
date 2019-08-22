import os
from html.parser import HTMLParser
from urllib.request import (Request, urlretrieve, urlopen)

#------------------------------------------------------------------------------------------------------------------------

class FullImagePageParser (HTMLParser):
    is_inside_correct_div = False
    image_url = ""
    type = "reddit"

    #------------------------------------------------------------------------------------------------------------------------

    def handle_starttag(self, tag, attributes):
        if self.type == "reddit":
            if tag == "div" and len(attributes) == 1 and attributes[0][1] == "media-preview-content":
                self.is_inside_correct_div = True
            elif self.is_inside_correct_div:
                self.image_url = attributes[0][1]
                raise Exception()
        elif self.type == "imgur":
            if tag == "link" and len(attributes) == 2 and attributes[0][1] == "image_src":
                self.image_url = attributes[1][1]
                raise Exception()

#------------------------------------------------------------------------------------------------------------------------

class SubredditParser (HTMLParser):
    # User input variables
    name_of_folder_to_save_to = None
    number_of_pages_to_download = None
    subreddit_url = None

    # Changing variables
    number_of_images_downloaded = 0
    number_of_pages_downloaded = 0
    current_url = None

    #------------------------------------------------------------------------------------------------------------------------
    
    def initialize (self):
        # A very nice welcome message
        
        print("\n---------------------------------------------------------------------------------------------------------")
        print("\nWelcome to the meme downloading service made by Björn Sundin!\nActually, you don't need to download memes, but whatever\n")

        #------------------------------------------------------------------------------------------------------------------------
        # Set subreddit url
        
        self.subreddit_url = input("Please enter the subreddit url: ")

        if self.subreddit_url == "":
            print("No input, will use r/wholesomesurrealmemes :^)")
            self.subreddit_url = "https://old.reddit.com/r/wholesomesurrealmemes/new/"
        else:
            if self.subreddit_url[:2] == "r/":
                self.subreddit_url = "https://old.reddit.com/" + self.subreddit_url              
            elif self.subreddit_url[:3] == "/r/":
                self.subreddit_url = "https://old.reddit.com/" + self.subreddit_url
            elif self.subreddit_url[:6] == "reddit":
                self.subreddit_url = "https://old." + self.subreddit_url
            elif self.subreddit_url[:4] == "www.":
                self.subreddit_url = "https://" + self.subreddit_url
            else:
                self.subreddit_url = "https://old.reddit.com/r/" + self.subreddit_url
                
        self.current_url = self.subreddit_url

        print()
        
        #------------------------------------------------------------------------------------------------------------------------
        # Set number of pages to download
        
        self.number_of_pages_to_download = input("Enter the number of pages of images to download: ")

        if self.number_of_pages_to_download == "":
            print("No input, will download one page of juicy memes.")
            self.number_of_pages_to_download = 1
        else:
            self.number_of_pages_to_download = int(self.number_of_pages_to_download)

        print()

        #------------------------------------------------------------------------------------------------------------------------

        # Set folder name
        self.name_of_folder_to_save_to = input("Enter the name of the folder to save to: ")
        if self.name_of_folder_to_save_to == "":
            print('No input, folder will be called "Subreddit images".')
            self.name_of_folder_to_save_to = "Subreddit images"

        # Create folder if it doesn't exist
        if not os.path.exists(self.name_of_folder_to_save_to):
            os.makedirs(self.name_of_folder_to_save_to)

        print()            

    #------------------------------------------------------------------------------------------------------------------------
    
    # Saves an image or goes to the next page
    def handle_starttag (self, tag, attributes):
        # if len(attributes) > 1 and attributes[0][1] == "_2_tDEnGMLxpM6uOa2kaDB3 media-element" and attributes[1][0] == "src":
        #     url = attributes[1][1]
        #     print("Image" + str(self.number_of_images_downloaded) + ": " + url)
        #     urlretrieve(url, self.name_of_folder_to_save_to + '/' + str(self.number_of_images_downloaded) + url[-4:])
        #     self.number_of_images_downloaded += 1
        if tag == "a" and len(attributes) > 2 and attributes[1][1] == "thumbnail":
            url = ""

            # If it's a linked image hosted on for example imgur, use that url.
            # Otherwise, go to the linked full image page and take the url of the image there.
            ending = attributes[2][1][-4:]
            if ending == ".png" or ending == ".jpg" or ending == ".gif":
                url = attributes[2][1]
            elif attributes[2][1][:3] == "/r/":
                # Create request for linked page
                request = Request("https://old.reddit.com" + attributes[2][1])
                request.add_header("User-agent", "Image downloader")

                # Find image
                full_image_parser = FullImagePageParser()
                try:
                    full_image_parser.feed(str(urlopen(request).read()))
                except:
                    url = full_image_parser.image_url
            elif attributes[2][1][:12] == "http://imgur" or attributes[2][1][:13] == "https://imgur":
                # Create request for linked page
                request = Request(attributes[2][1])
                request.add_header("User-agent", "Image downloader")

                # Find image
                full_image_parser = FullImagePageParser()
                full_image_parser.type = "imgur"
                try:
                    full_image_parser.feed(str(urlopen(request).read()))
                except:
                    url = full_image_parser.image_url
            
            if url == "":
                print("Couldn't find image at " + attributes[2][1])
            else: 
                print("Image " + str(self.number_of_images_downloaded) + ": " + url)
                urlretrieve(url, self.name_of_folder_to_save_to + '/' + str(self.number_of_images_downloaded) + url[-4:])
                self.number_of_images_downloaded += 1
        
        # If this tag has the properties of a "next page" link, we
        # go to the next page by setting the url to the href attribute
        elif tag == 'a' and len(attributes) == 2 and attributes[0][0] == "href" and attributes[1][0] == "rel" and attributes[1][1] == "nofollow next":
            self.current_url = attributes[0][1]

#########################################################################################################################

def main ():
    subreddit_parser = SubredditParser()
    subreddit_parser.initialize()

    print("Downloading memes...\n")

    while subreddit_parser.number_of_pages_downloaded < subreddit_parser.number_of_pages_to_download:
        # Create request
        request = Request(subreddit_parser.current_url)
        request.add_header("User-agent", "Image downloader")

        # Feed the subreddit parser a page
        url_before = subreddit_parser.current_url

        subreddit_parser.feed(str(urlopen(request).read()))

        print("\nI've now downloaded page " + str(subreddit_parser.number_of_pages_downloaded) + ".\n")
        subreddit_parser.number_of_pages_downloaded += 1

        #------------------------------------------------------------------------------------------------------------------------
    
        if url_before == subreddit_parser.current_url:
            print("There were only " + str(subreddit_parser.number_of_pages_downloaded) + "/" + str(subreddit_parser.number_of_pages_to_download) + " pages of images available on that subreddit page, I'm sorry :^(")
            break
    
    print("\nYou've deserved the memes. Please come back soon for more")
    print("\n---------------------------------------------------------------------------------------------------------\n")

    input()

if __name__ == "__main__":
    main()
