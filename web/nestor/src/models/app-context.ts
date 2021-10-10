import { IotDevice, IotDeviceGroup } from '@models';
import { createContext } from 'react';
import { Socket } from 'socket.io-client';
import { DefaultEventsMap } from 'socket.io-client/build/typed-events';

export type AppContextType = {
    socket?: Socket<DefaultEventsMap, DefaultEventsMap>;
    devices: IotDevice[];
    selectedGroup?: IotDeviceGroup;
};

export const AppContextInit: AppContextType = { devices: [] };

export const AppContext = createContext(AppContextInit);
