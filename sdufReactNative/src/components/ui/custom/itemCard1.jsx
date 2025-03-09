import React, { memo } from 'react';
import { Image, StyleSheet, View, Text, FlatList } from 'react-native';
import uuid from 'react-native-uuid';
import Label1 from './label1';
import Label2 from './label2';
import CustomTouchableOpacity from '../../helpers/touchableOpacity';

function ItemCard1({ data }) {
  const renderLabel = ({ item }) => <Label2 data={{ text: item.text }} />;
  const renderPrice = ({ item }) => (
    <Text style={[styles.price_usd]}>
      {item} {data.price[item]}
    </Text>
  );
  const renderCharacteristics = ({ item }) => (
    <View>
      <Label1 data={{ text: item.text, src: item.src }} />
    </View>
  );
  return (
    <View>
      {data ? (
        <>
          <CustomTouchableOpacity data={data}>
            <View style={[styles.wrap_img]}>
              <Image
                resizeMode={'cover'}
                style={[styles.image, { width: '100%', height: 200 }]}
                source={{ uri: data.src }}
              />
            </View>
            <View style={[styles.wrap_info]}>
              <Text style={[styles.title]}>{data.title}</Text>
              {data.price ? (
                <View style={[styles.prices_list]}>
                  <FlatList
                    data={Object.keys(data.price)}
                    numColumns={5}
                    renderItem={renderPrice}
                    listKey={uuid.v4()}
                    keyExtractor={(item) => item.id}
                  />
                </View>
              ) : null}

              <FlatList
                style={[styles.labels]}
                data={data.labels}
                numColumns={2}
                renderItem={renderLabel}
                listKey={uuid.v4()}
                keyExtractor={(item) => uuid.v4()}
              />
              <FlatList
                style={[styles.characteristics]}
                columnWrapperStyle={{ paddingRight: 5 }}
                data={data.characteristics}
                numColumns={2}
                renderItem={renderCharacteristics}
                listKey={uuid.v4()}
                keyExtractor={(item) => uuid.v4()}
              />
            </View>
          </CustomTouchableOpacity>
        </>
      ) : null}
    </View>
  );
}

export default memo(ItemCard1);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  image: {
    maxHeight: 300,
  },
  title: {
    fontSize: 20,
    alignItems: 'center',
  },
  prices_list: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    paddingBottom: 3,
  },
  price: {
    fontSize: 22,
  },
  price_usd: {
    color: 'green',
    fontWeight: 'bold',
    paddingRight: 10,
    fontSize: 20,
  },
  labels: {
    paddingBottom: 3,
  },
  characteristics: {
    paddingBottom: 3,
  },
  wrap_info: {
    paddingLeft: '5%',
    paddingRight: '5%',
  },
  wrap_img: {
    paddingBottom: 7,
  },
});
