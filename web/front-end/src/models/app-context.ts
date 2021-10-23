import { IotDevice, IotDeviceGroup, SocketType, Store, StoreInit } from '@models';
import { createContext } from 'react';

export type AppContextType = {
    socket: SocketType;
    store: Store;
};

export const AppContextInit: AppContextType = {
    socket: undefined,
    store: StoreInit,
};

export const AppContext = createContext(AppContextInit);
