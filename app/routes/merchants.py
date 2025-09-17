# app/routes/merchants.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from services.clover_api import get_clover_categories, get_clover_items
from schemas.category import Category, Variation, CloverItem
from dependencies import get_clover_token # Import the correct dependency
from pydantic import BaseModel
from database.database import get_db
from sqlalchemy.orm import Session
from models.merchant import Merchant as MerchantModel

router = APIRouter()
# Add this Pydantic schema for the response
class MerchantInfo(BaseModel):
    db_id: int
    clover_merchant_id: str
    name: str

    class Config:
        form_attribute = True

@router.get("/merchants", response_model=List[MerchantInfo])
def list_all_merchants(db: Session = Depends(get_db)):
    """
    Retrieves a list of all merchants from the database.
    """
    merchants = db.query(MerchantModel).all()
    return merchants

@router.get("/merchants/{merchant_id}/categories", response_model=List[Category])
async def get_merchant_categories_from_clover(
    merchant_id: str,
    access_token: str = Depends(get_clover_token) # Use the correct dependency
):
    """
    Retrieves all categories and their variations for a specific merchant
    by fetching data directly from the Clover API.
    """
    # 1. Fetch all categories and items from Clover using the retrieved token
    clover_categories_data = await get_clover_categories(merchant_id, access_token)
    clover_items_data = await get_clover_items(merchant_id, access_token)

    # 2. Process the data into the desired response format
    # Create a dictionary to hold category data for easy lookup
    categories_map = {
        cat['id']: Category(id=cat['id'], name=cat['name'], variations=[])
        for cat in clover_categories_data.get('elements', [])
    }

    # Loop through items and assign them (and their variations) to the correct categories
    for item_data in clover_items_data.get('elements', []):
        item = CloverItem(**item_data)
        
        # Check if the item is associated with any categories
        if item.categories and item.categories.get('elements'):
            for category_ref in item.categories['elements']:
                category_id = category_ref['id']
                
                if category_id in categories_map:
                    # If the item has variants, add each as a variation
                    if item.variants:
                        for variant_data in item.variants:
                            variation = Variation(
                                id=variant_data.id,
                                name=f"{item.name} ({variant_data.name})",
                                # Clover API returns price in cents, so convert to dollars
                                price=variant_data.price / 100.0
                            )
                            categories_map[category_id].variations.append(variation)
                    # If no variants, the item itself is the variation
                    else:
                        variation = Variation(
                            id=item.id,
                            name=item.name,
                            price=item.price / 100.0
                        )
                        categories_map[category_id].variations.append(variation)

    # Return the list of category objects
    return list(categories_map.values())

