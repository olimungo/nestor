import { IotDevice } from '@models';
import { createContext } from 'react';
import { Socket } from 'socket.io-client';
import { DefaultEventsMap } from 'socket.io-client/build/typed-events';
// import { DevicesByTagsType, DeviceType } from '@models';

export type AppContextType = {
    socket?: Socket<DefaultEventsMap, DefaultEventsMap>;
    devices?: IotDevice[];
    // selectedDevices?: DevicesByTagsType;
};

export const AppContextInit: AppContextType = {};

export const AppContext = createContext(AppContextInit);
