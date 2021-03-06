import bson
import pandas as pd

def ingest_bson(encoded_str):

    raw_list = encoded_str.split('-')
    map_object = map(int, raw_list)
    list_of_integers = list(map_object)
    bson_raw = bytearray(list_of_integers)
    b = bson.loads(bson_raw)
    return b
    
def main():
    df = pd.read_csv('/home/marcos/BSON_embedding/build/result.csv')
    src = df['BSON'][0]
    print(len(src))
    b = ingest_bson(src)    
    print(b['data'][0]['x'])

if __name__ == "__main__":
    main()

'''
for i,row in df.iterrows():
    if row['New_Category'] == 'vial' or row['New_Category'] == 'villa' or row['New_Category'] == 'palo' or row['New_Category'] == 'doble' or row['New_Category'] == 'otro':
        df.loc[i,'clase_str'] = row['New_Category']
        print('a')
'''
