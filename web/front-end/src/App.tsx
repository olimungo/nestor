import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import { AppContext, IotDevice, SocketType, Store, StoreInit } from '@models';
import { AppFooter, AppHeader } from '@components';
import { Redirect, Route, Switch } from 'react-router';
import { Commands, Controls, Devices, EditDevice, Tags } from '@pages';

function App() {
    const [socket, setSocket] = useState<SocketType>();
    const [store, setStore] = useState<Store>(StoreInit);
    const [devices, setDevices] = useState<IotDevice[]>([]);
    const sortIotDevice = (a: IotDevice, b: IotDevice) => (a.id > b.id ? 1 : -1);

    useEffect(() => {
        const domain = `ws://${window.location.hostname}:${process.env.REACT_APP_WEBSOCKETS_PORT}`;
        const socket = io(domain);

        setSocket(socket);

        const gotDevices = (devices: IotDevice[]) => {
            const sortedDevices = devices.sort(sortIotDevice);

            setStore((previousStore) => {
                previousStore.devices = sortedDevices;
                return previousStore;
            });

            // The command below has no use, but without it the store doesn't get updated in components
            setDevices(sortedDevices);
        };

        socket.on('devices', gotDevices);

        socket.emit('get-devices');

        return () => {
            socket.off('devices', gotDevices);
        };
    }, []);

    return (
        <>
            <AppContext.Provider value={{ socket, store }}>
                <div className="h-100 w-100 text-white" style={{ maxWidth: '70rem' }}>
                    <div className="flex flex-col items-center h-full md:w-12/12">
                        <div className="w-full">
                            <AppHeader />
                        </div>

                        <div
                            className="w-full flex-grow overflow-auto bg-white"
                            style={{ backgroundColor: '#1f263d' }}
                        >
                            <Switch>
                                <Route path="/commands">
                                    <Commands />
                                </Route>

                                <Route path="/tags">
                                    <Tags />
                                </Route>

                                <Route path="/devices/:urlId">
                                    <EditDevice />
                                </Route>

                                <Route path="/devices">
                                    <Devices />
                                </Route>

                                <Route path="/controls">
                                    <Controls />
                                </Route>

                                <Route path="/">
                                    <Redirect to="/tags" />
                                </Route>
                            </Switch>
                        </div>

                        <div className="w-full">
                            <AppFooter />
                        </div>
                    </div>
                </div>
            </AppContext.Provider>
        </>
    );
}

export default App;
