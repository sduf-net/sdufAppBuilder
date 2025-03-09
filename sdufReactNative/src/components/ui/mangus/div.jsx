import * as React from 'react';
import { VirtualizedList } from 'react-native';
import { Div } from 'react-native-magnus';
import { getItem, getItemCount } from '../../../utils';

const DivWidget = (config) => {
  const renderWidget = ({ item }) => <config.factory props={item} />;

  return (
    <Div {...config.data.props}>
      <VirtualizedList
        data={config.nestedComponents}
        renderItem={renderWidget}
        keyExtractor={(item) => item.id}
        getItemCount={getItemCount}
        getItem={getItem}
      />
    </Div>
  );
};

export default DivWidget;
