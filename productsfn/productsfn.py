import io
import json
import logging
from typing import final
from bs4 import BeautifulSoup
import requests

from fdk import response

# import oci.object_storage


def handler(ctx, data: io.BytesIO = None):
    try:
        body = json.loads(data.getvalue())
        url = body["url"]
    except (Exception, ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))

    logging.getLogger().info("Inside Python Product Scraping function")

    #resp = put_object("scraping-data","Test",finalScrape(url))
    return response.Response(
        ctx,
        response_data=finalScrape(url),
        headers={"Content-Type": "application/json"}
    )


def scrapeProducts(url,pageId):
    r = requests.get("https://"+url + f"/products.json?limit=250&page={pageId}")
    if(r.status_code!=200):
        return
    else:
        if(len(r.json()['products'])):
            data = r.json()['products']
            return (data)
        else:
            return

def parseProductData(jsondata):
    Products=[]
    if jsondata is not None:
       for product in jsondata:
            soup = BeautifulSoup(product['body_html'],"lxml")
            Product={    
                'productId' : product['id'],
                'productTitle' : product['title'],
                'productHandle' : product['handle'],
                'productDesc' : soup.get_text(),
                'productType'  : product['product_type'],
                'productTags' : product['tags'],
                'productPublishedDate':product['published_at']
                }
            Products.append(Product)
    return (Products)

def finalScrape(url):
    allProducts=[]
    for page in range(1,10):
        allProducts.append(parseProductData(scrapeProducts(url,page)))
    return {k:v for k,v in enumerate(allProducts) }

# def put_object(bucketName, objectName, content):
#     signer = oci.auth.signers.get_resource_principals_signer()
#     client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
#     namespace = client.get_namespace().data
#     output=""
#     try:
#         object = client.put_object(namespace, bucketName, objectName, json.dumps(content))
#         output = "Success: Put object '" + objectName + "' in bucket '" + bucketName + "'"
#     except Exception as e:
#         output = "Failed: " + str(e.message)
#     return { "state": output }

