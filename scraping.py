# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd 
import datetime as dt 

def scrape_all():
    # Initiate headless driver
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    # Since these are pairs 
    news_title, news_paragraph= mars_news(browser)
    hemisphere_image_urls=hemisphere(browser)
    # Run all scraping functions and store results in dictionary 
    data={
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_image_urls,
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


## > SCRAPE MARS NEWS <

def mars_news(browser):

    # visit NASA website 
    url= 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)


    # searching for elements with a specific combination of tag (ul) and (li) and attriobute (item_lit) and (slide)
   
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # HTML Parser. Convert the brpwser html to a soup object and then quit the browser
    html= browser.html 
    news_soup= soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        #slide_elem looks for <ul /> tags and descendents <li />
       
        slide_elem= news_soup.select_one('ul.item_list li.slide')
        # Get Title
        news_title=slide_elem.find('div', class_= 'content_title').get_text()
        # Get article body
        news_p= slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None,None

    return news_title, news_p


## > SCRAPE FEATURED IMAGES <

def featured_image(browser):

    # Visit URL 
    url= 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full_image button
    full_image_elem= browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Find the more info button and click that 
    browser.is_element_present_by_text('more info', wait_time=1)

    # will take our string 'more info' and add link associated with it, then click
    more_info_elem=browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html=browser.html
    img_soup=soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        
        img_url_rel= img_soup.select_one('figure.lede a img').get("src")
    
    except AttributeError:
        return None
    # Need to get the FULL URL: Only had relative path before
    img_url= f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url


## > SCRAPE FACTS ABOUT MARS <

def mars_facts():
    
    # Add try/except for error handling
    try:
        # Creating DF by telling function to look for first html table in site it encounters by indexing it to zero
        df=pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    # BaseException, catches multiple types of errors
    except BaseException:
        return None
    
    # Assigning columns, and set 'description' as index 
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    #Convert back to HTML format, add bootstrap
    return df.to_html()


## > SCRAPE HEMISPHERE <

def hemisphere(browser):
    url= 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)


    hemisphere_image_urls = []

    imgs_links= browser.find_by_css("a.product-item h3")

    for x in range(len(imgs_links)):
        hemisphere={}

        # Find elements going to click link 
        browser.find_by_css("a.product-item h3")[x].click()

        # Find sample Image link
        sample_img= browser.find_link_by_text("Sample").first
        hemisphere['img_url']=sample_img['href']

        # Get hemisphere Title
        hemisphere['title']=browser.find_by_css("h2.title").text

        #Add Objects to hemisphere_img_urls list
        hemisphere_image_urls.append(hemisphere)

        # Go Back
        browser.back()
    return hemisphere_image_urls

if __name__== "__main__":
    # If running as script, print scrapped data
    print(scrape_all())
