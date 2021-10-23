import { Socket } from 'socket.io-client';
import { DefaultEventsMap } from 'socket.io-client/build/typed-events';

export type SocketType = Socket<DefaultEventsMap, DefaultEventsMap> | undefined;
