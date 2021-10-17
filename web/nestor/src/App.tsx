import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import { AppContext, IotDevice, SocketType, Store, StoreInit } from '@models';
import { AppFooter, AppHeader } from '@components';
import { Redirect, Route, Switch } from 'react-router';
import { Commands, Controls, Devices, EditDevice, Tags } from '@pages';

function App() {
    const [devices, setDevices] = useState<IotDevice[]>([]);
    const [socket, setSocket] = useState<SocketType>();
    const [store, setStore] = useState<Store>(StoreInit);
    const sortIotDevice = (a: IotDevice, b: IotDevice) => (a.id > b.id ? 1 : -1);

    useEffect(() => {
        const socket = io(process.env.REACT_APP_WEBSOCKETS || 'ws://localhost:3001');

        setSocket(socket);

        const gotDevices = (devices: IotDevice[]) => {
            const sortedDevices = devices.sort(sortIotDevice);

            setStore((previous) => {
                previous.devices = sortedDevices;
                return previous;
            });

            setDevices(sortedDevices);
        };

        const updateDevice = (updatedDevice: IotDevice) =>
            setDevices((devices) => {
                const filtered = devices.filter((device) => device.id !== updatedDevice.id);
                return [...filtered, updatedDevice].sort(sortIotDevice);
            });
        const removeDevice = (deviceToRemoveId: string) =>
            setDevices((devices) =>
                devices.filter((device) => device.id !== deviceToRemoveId).sort(sortIotDevice)
            );

        socket.on('devices', gotDevices);
        socket.on('update-device', updateDevice);
        socket.on('remove-device', removeDevice);

        socket.emit('get-devices');

        return () => {
            socket.off('devices', gotDevices);
            socket.off('update-device', updateDevice);
            socket.off('remove-device', removeDevice);
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
