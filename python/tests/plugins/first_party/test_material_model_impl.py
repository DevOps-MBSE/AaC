from unittest import TestCase
from tempfile import TemporaryDirectory

from aac.plugins.first_party.material_model.material_model_impl import gen_bom

from tests.helpers.assertion import assert_plugin_success, assert_validation_failure
from tests.helpers.io import new_working_dir, temporary_test_file


class TestMaterialModel(TestCase):
    def test_gen_bom(self):
        with (
            TemporaryDirectory() as temp_dir,
            temporary_test_file(VALID_MATERIAL_MODEL, dir=temp_dir) as temp_arch_file,
            new_working_dir(temp_dir),
        ):
            result = gen_bom(temp_arch_file.name, temp_dir)
            assert_plugin_success(result)

            # assert BOM was actually written
            with open("bom.csv") as bom_csv_file:
                # it's not clear what does and doesn't get quoted by the CSV writer, so eliminate quotes
                bom_csv_contents = bom_csv_file.read().replace('"', "")

                # Assert csv contents are present
                self.assertIn("name,make,model,description,quantity,unit_cost,total_cost,need_date,location", bom_csv_contents)
                self.assertIn(
                    "My_New_Apartment / Kitchen / Appliances / Blender,Grind House,Liquificationinator 1000,7 setting industrial strength blender with pulse,1,99.99,99.99,,Crystal Terrace Apartments Unit 1234 / The room with the sink and the stove",
                    bom_csv_contents,
                )

    def test_gen_bom_circular_reference(self):
        with TemporaryDirectory() as temp_dir, temporary_test_file(CIRCULAR_DEPLOYMENT_REF) as temp_arch_file:
            result = gen_bom(temp_arch_file.name, temp_dir)
            assert_validation_failure(result)

    def test_gen_bom_bad_reference(self):
        with TemporaryDirectory() as temp_dir, temporary_test_file(BAD_MATERIAL_REFERENCE) as temp_arch_file:
            result = gen_bom(temp_arch_file.name, temp_dir)
            assert_validation_failure(result)


VALID_MATERIAL_MODEL = """
deployment:
  name: My_New_Apartment
  description: The place I'm going to live.
  location: Crystal Terrace Apartments Unit 1234
  sub-deployments:
    - deployment-ref: Living_Room
      quantity: 1
    - deployment-ref: Kitchen
      quantity: 1
---
deployment:
  name: Living_Room
  description:  The place I'll hang out a lot.
  location: The large room off the entry way
  assemblies:
    - assembly-ref: Entertainment_System
      quantity: 1
    - assembly-ref: Seating_Area
      quantity: 1
---
deployment:
  name: Kitchen
  description:  Where I'll cook my food.
  location: The room with the sink and the stove
  assemblies:
    - assembly-ref: Appliances
      quantity: 1
    - assembly-ref: Cook_Ware
      quantity: 1
---
assembly:
  name: Seating_Area
  description:  The place I'll hang out a lot.
  parts:
    - part-ref: Couch
      quantity: 1
    - part-ref: Arm_Chair
      quantity: 1
    - part-ref: Coffee_Table
      quantity: 1
    - part-ref: Side_Table
      quantity: 2
    - part-ref: Table_Lamp
      quantity: 2
    - part-ref: Coasters
      quantity: 1
---
assembly:
  name: Entertainment_System
  description:  Mostly electronic toys
  parts:
    - part-ref: TV
      quantity: 1
    - part-ref: Sound_Bar
      quantity: 1
    - part-ref: X_Box
      quantity: 1
    - part-ref: Wifi_Router
      quantity: 1
---
assembly:
  name: Appliances
  description: Things that make a kitchen work.
  parts:
    - part-ref: Refrigerator
      quantity: 1
    - part-ref: Stove
      quantity: 1
    - part-ref: Dish_Washer
      quantity: 1
    - part-ref: Coffee_Pot
      quantity: 1
    - part-ref: Blender
      quantity: 1
---
assembly:
  name: Cook_Ware
  description:  Pots, pans, and such.
  parts:
    - part-ref: Pans
      quantity: 1
    - part-ref: Dishes
      quantity: 1
    - part-ref: Utensils
      quantity: 1
    - part-ref: Silverware
      quantity: 1
---
part:
  name: Coasters
  make: HUAOAO
  model: Cork Coaster Set
  description: Set of 12 plain cork coasters.
  unit_cost: 7.19
  quote_type: Web_Reference
  quote: https://smile.amazon.com/Coaster-Absorbent-Resistant-Reusable-Coasters/dp/B08PZ15J2N
---
part:
  name: TV
  make: Samsung
  model: S-Z452-OG2331-55-HD
  description: 55 inch high-definition smart tv
  unit_cost: 682.23
  quote_type: Web_Reference
  quote: https://www.google.com
---
part:
  name: Wifi_Router
  make: NetGear
  model: N334521939
  description: 802.11 a/b/g
  unit_cost: 88.33
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Sound_Bar
  make: Loudness Inc
  model: LI-35-ST-HDMI-BT-334
  description: Something better than the built-in tv speakers
  unit_cost: 120.23
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: X_Box
  make: Microsoft
  model: X-Box One v2
  description: Streaming and gaming device
  unit_cost: 599.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Coffee_Pot
  make: Perky Mornings
  model: Dual-brew 2200
  description: Coffee maker with drip and k-cup
  unit_cost: 199.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Blender
  make: Grind House
  model: Liquificationinator 1000
  description: 7 setting industrial strength blender with pulse
  unit_cost: 99.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Pans
  make: Affordable Living
  model: 12-al-33288
  description: 12 piece aluminum pots and pans
  unit_cost: 299.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Dishes
  make: Affordable Living
  model: 2251-AHRSU-8
  description: 8 place setting dinner ware set
  unit_cost: 129.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Utensils
  make: Affordable Living
  model: XG-33445
  description: Complete set of knives, spatulas, measuring cups, and whisks
  unit_cost: 99.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Silverware
  make: Affordable Living
  model: 8835-AHTTR-12
  description: 12 settings of fork, spoon, and butter knife
  unit_cost: 139.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Refrigerator
  make: General Electric
  model: Chill Box Mark 2
  description: Standard over under fridge
  unit_cost: 0.01
  quote_type: Furnished_Equipment
  quote: ./terms_of_lease.pdf
---
part:
  name: Stove
  make: General Electric
  model: Kitchen Cooker Mark 2
  description: Standard 4 eye electric stove with oven
  unit_cost: 0.01
  quote_type: Furnished_Equipment
  quote: ./terms_of_lease.pdf
---
part:
  name: Dish_Washer
  make: General Electric
  model: Scrubinator Mark 2
  description: Standard 2 rack dish washer
  unit_cost: 0.01
  quote_type: Furnished_Equipment
  quote: ./terms_of_lease.pdf
---
part:
  name: Couch
  make: Furniture_Fair
  model: Comfort Couch 3000
  description: 3 cushion plush couch with pillows.
  unit_cost: 750.26
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Arm_Chair
  make: Furniture_Fair
  model: Comfort Chair 3000
  description: Reclining chair with cup holder
  unit_cost: 599.99
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Coffee_Table
  make: Furniture_Fair
  model: Comfort Coffee Table 3000
  description: Coffee table with glass inlay
  unit_cost: 149.97
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Side_Table
  make: Furniture_Fair
  model: Comfort Side Table 3000
  description: Side table with glass inlay
  unit_cost: 98.96
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Table_Lamp
  make: Furniture_Fair
  model: Light Bringer 3000
  description: Classic modern lamp with shade and USB power outlets
  unit_cost: 42.55
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
"""

CIRCULAR_DEPLOYMENT_REF = """
deployment:
  name: My_New_Apartment
  description: The place I'm going to live.
  location: Crystal Terrace Apartments Unit 1234
  sub-deployments:
    - deployment-ref: Living_Room
      quantity: 1
    - deployment-ref: Kitchen
      quantity: 1
---
deployment:
  name: Living_Room
  description:  The place I'll hang out a lot.
  location: The large room off the entry way
  sub-deployments:
    - deployment-ref: My_New_Apartment
      quantity: 1
  assemblies:
    - assembly-ref: Entertainment_System
      quantity: 1
    - assembly-ref: Seating_Area
      quantity: 1
---
deployment:
  name: Kitchen
  description:  Where I'll cook my food.
  location: The room with the sink and the stove
  assemblies:
    - assembly-ref: Appliances
      quantity: 1
    - assembly-ref: Cook_Ware
      quantity: 1
---
assembly:
  name: Seating_Area
  description:  The place I'll hang out a lot.
  parts:
    - part-ref: Couch
      quantity: 1
    - part-ref: Arm_Chair
      quantity: 1
    - part-ref: Coffee_Table
      quantity: 1
    - part-ref: Side_Table
      quantity: 2
    - part-ref: Table_Lamp
      quantity: 2
    - part-ref: Coasters
      quantity: 1
---
assembly:
  name: Entertainment_System
  description:  Mostly electronic toys
  parts:
    - part-ref: TV
      quantity: 1
    - part-ref: Sound_Bar
      quantity: 1
    - part-ref: X_Box
      quantity: 1
    - part-ref: Wifi_Router
      quantity: 1
---
assembly:
  name: Appliances
  description: Things that make a kitchen work.
  parts:
    - part-ref: Refrigerator
      quantity: 1
    - part-ref: Stove
      quantity: 1
    - part-ref: Dish_Washer
      quantity: 1
    - part-ref: Coffee_Pot
      quantity: 1
    - part-ref: Blender
      quantity: 1
---
assembly:
  name: Cook_Ware
  description:  Pots, pans, and such.
  parts:
    - part-ref: Pans
      quantity: 1
    - part-ref: Dishes
      quantity: 1
    - part-ref: Utensils
      quantity: 1
    - part-ref: Silverware
      quantity: 1
---
part:
  name: Coasters
  make: HUAOAO
  model: Cork Coaster Set
  description: Set of 12 plain cork coasters.
  unit_cost: 7.19
  quote_type: Web_Reference
  quote: https://smile.amazon.com/Coaster-Absorbent-Resistant-Reusable-Coasters/dp/B08PZ15J2N
---
part:
  name: TV
  make: Samsung
  model: S-Z452-OG2331-55-HD
  description: 55 inch high-definition smart tv
  unit_cost: 682.23
  quote_type: Web_Reference
  quote: https://www.google.com
---
part:
  name: Wifi_Router
  make: NetGear
  model: N334521939
  description: 802.11 a/b/g
  unit_cost: 88.33
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Sound_Bar
  make: Loudness Inc
  model: LI-35-ST-HDMI-BT-334
  description: Something better than the built-in tv speakers
  unit_cost: 120.23
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: X_Box
  make: Microsoft
  model: X-Box One v2
  description: Streaming and gaming device
  unit_cost: 599.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Coffee_Pot
  make: Perky Mornings
  model: Dual-brew 2200
  description: Coffee maker with drip and k-cup
  unit_cost: 199.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Blender
  make: Grind House
  model: Liquificationinator 1000
  description: 7 setting industrial strength blender with pulse
  unit_cost: 99.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Pans
  make: Affordable Living
  model: 12-al-33288
  description: 12 piece aluminum pots and pans
  unit_cost: 299.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Dishes
  make: Affordable Living
  model: 2251-AHRSU-8
  description: 8 place setting dinner ware set
  unit_cost: 129.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Utensils
  make: Affordable Living
  model: XG-33445
  description: Complete set of knives, spatulas, measuring cups, and whisks
  unit_cost: 99.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Silverware
  make: Affordable Living
  model: 8835-AHTTR-12
  description: 12 settings of fork, spoon, and butter knife
  unit_cost: 139.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Refrigerator
  make: General Electric
  model: Chill Box Mark 2
  description: Standard over under fridge
  unit_cost: 0.01
  quote_type: Furnished_Equipment
  quote: ./terms_of_lease.pdf
---
part:
  name: Stove
  make: General Electric
  model: Kitchen Cooker Mark 2
  description: Standard 4 eye electric stove with oven
  unit_cost: 0.01
  quote_type: Furnished_Equipment
  quote: ./terms_of_lease.pdf
---
part:
  name: Dish_Washer
  make: General Electric
  model: Scrubinator Mark 2
  description: Standard 2 rack dish washer
  unit_cost: 0.01
  quote_type: Furnished_Equipment
  quote: ./terms_of_lease.pdf
---
part:
  name: Couch
  make: Furniture_Fair
  model: Comfort Couch 3000
  description: 3 cushion plush couch with pillows.
  unit_cost: 750.26
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Arm_Chair
  make: Furniture_Fair
  model: Comfort Chair 3000
  description: Reclining chair with cup holder
  unit_cost: 599.99
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Coffee_Table
  make: Furniture_Fair
  model: Comfort Coffee Table 3000
  description: Coffee table with glass inlay
  unit_cost: 149.97
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Side_Table
  make: Furniture_Fair
  model: Comfort Side Table 3000
  description: Side table with glass inlay
  unit_cost: 98.96
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Table_Lamp
  make: Furniture_Fair
  model: Light Bringer 3000
  description: Classic modern lamp with shade and USB power outlets
  unit_cost: 42.55
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
"""

BAD_MATERIAL_REFERENCE = """
deployment:
  name: My_New_Apartment
  description: The place I'm going to live.
  location: Crystal Terrace Apartments Unit 1234
  sub-deployments:
    - deployment-ref: Living_Room
      quantity: 1
    - deployment-ref: Kitchen
      quantity: 1
---
deployment:
  name: Living_Room
  description:  The place I'll hang out a lot.
  location: The large room off the entry way
  assemblies:
    - assembly-ref: Entertainment_System
      quantity: 1
    - assembly-ref: Seating_Area
      quantity: 1
---
deployment:
  name: Kitchen
  description:  Where I'll cook my food.
  location: The room with the sink and the stove
  assemblies:
    - assembly-ref: Appliances
      quantity: 1
    - assembly-ref: Cook_Ware
      quantity: 1
---
assembly:
  name: Seating_Area
  description:  The place I'll hang out a lot.
  parts:
    - part-ref: Couch
      quantity: 1
    - part-ref: Arm_Chair_BROKEN
      quantity: 1
    - part-ref: Coffee_Table
      quantity: 1
    - part-ref: Side_Table
      quantity: 2
    - part-ref: Table_Lamp
      quantity: 2
    - part-ref: Coasters
      quantity: 1
---
assembly:
  name: Entertainment_System
  description:  Mostly electronic toys
  parts:
    - part-ref: TV
      quantity: 1
    - part-ref: Sound_Bar
      quantity: 1
    - part-ref: X_Box
      quantity: 1
    - part-ref: Wifi_Router
      quantity: 1
---
assembly:
  name: Appliances
  description: Things that make a kitchen work.
  parts:
    - part-ref: Refrigerator
      quantity: 1
    - part-ref: Stove
      quantity: 1
    - part-ref: Dish_Washer
      quantity: 1
    - part-ref: Coffee_Pot
      quantity: 1
    - part-ref: Blender
      quantity: 1
---
assembly:
  name: Cook_Ware
  description:  Pots, pans, and such.
  parts:
    - part-ref: Pans
      quantity: 1
    - part-ref: Dishes
      quantity: 1
    - part-ref: Utensils
      quantity: 1
    - part-ref: Silverware
      quantity: 1
---
part:
  name: Coasters
  make: HUAOAO
  model: Cork Coaster Set
  description: Set of 12 plain cork coasters.
  unit_cost: 7.19
  quote_type: Web_Reference
  quote: https://smile.amazon.com/Coaster-Absorbent-Resistant-Reusable-Coasters/dp/B08PZ15J2N
---
part:
  name: TV
  make: Samsung
  model: S-Z452-OG2331-55-HD
  description: 55 inch high-definition smart tv
  unit_cost: 682.23
  quote_type: Web_Reference
  quote: https://www.google.com
---
part:
  name: Wifi_Router
  make: NetGear
  model: N334521939
  description: 802.11 a/b/g
  unit_cost: 88.33
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Sound_Bar
  make: Loudness Inc
  model: LI-35-ST-HDMI-BT-334
  description: Something better than the built-in tv speakers
  unit_cost: 120.23
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: X_Box
  make: Microsoft
  model: X-Box One v2
  description: Streaming and gaming device
  unit_cost: 599.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Coffee_Pot
  make: Perky Mornings
  model: Dual-brew 2200
  description: Coffee maker with drip and k-cup
  unit_cost: 199.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Blender
  make: Grind House
  model: Liquificationinator 1000
  description: 7 setting industrial strength blender with pulse
  unit_cost: 99.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Pans
  make: Affordable Living
  model: 12-al-33288
  description: 12 piece aluminum pots and pans
  unit_cost: 299.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Dishes
  make: Affordable Living
  model: 2251-AHRSU-8
  description: 8 place setting dinner ware set
  unit_cost: 129.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Utensils
  make: Affordable Living
  model: XG-33445
  description: Complete set of knives, spatulas, measuring cups, and whisks
  unit_cost: 99.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Silverware
  make: Affordable Living
  model: 8835-AHTTR-12
  description: 12 settings of fork, spoon, and butter knife
  unit_cost: 139.99
  quote_type: Web_Reference
  quote: https://smile.amazon.com
---
part:
  name: Refrigerator
  make: General Electric
  model: Chill Box Mark 2
  description: Standard over under fridge
  unit_cost: 0.01
  quote_type: Furnished_Equipment
  quote: ./terms_of_lease.pdf
---
part:
  name: Stove
  make: General Electric
  model: Kitchen Cooker Mark 2
  description: Standard 4 eye electric stove with oven
  unit_cost: 0.01
  quote_type: Furnished_Equipment
  quote: ./terms_of_lease.pdf
---
part:
  name: Dish_Washer
  make: General Electric
  model: Scrubinator Mark 2
  description: Standard 2 rack dish washer
  unit_cost: 0.01
  quote_type: Furnished_Equipment
  quote: ./terms_of_lease.pdf
---
part:
  name: Couch
  make: Furniture_Fair
  model: Comfort Couch 3000
  description: 3 cushion plush couch with pillows.
  unit_cost: 750.26
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Arm_Chair
  make: Furniture_Fair
  model: Comfort Chair 3000
  description: Reclining chair with cup holder
  unit_cost: 599.99
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Coffee_Table
  make: Furniture_Fair
  model: Comfort Coffee Table 3000
  description: Coffee table with glass inlay
  unit_cost: 149.97
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Side_Table
  make: Furniture_Fair
  model: Comfort Side Table 3000
  description: Side table with glass inlay
  unit_cost: 98.96
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
---
part:
  name: Table_Lamp
  make: Furniture_Fair
  model: Light Bringer 3000
  description: Classic modern lamp with shade and USB power outlets
  unit_cost: 42.55
  quote_type: Vendor_Quote
  quote: ./furniture_fair_quote.pdf
"""
