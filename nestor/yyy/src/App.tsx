import { useEffect, useRef, useState } from 'react';
import { Switch, Route, Redirect, useHistory } from 'react-router-dom';
import { io } from 'socket.io-client';
import { AppHeader, AppFooter } from '@components';
import { AppContext, DevicesByTagsType, DeviceType } from '@declarations';
import { Commands, Controls, Devices, EditDevice, Search, Tags } from '@pages';

function App() {
    const history = useHistory();
    const init = useRef(true);
    const [devices, setDevices] = useState<DeviceType[]>([]);
    const [selectedDevices, setSelectedDevices] = useState<DevicesByTagsType>();

    const socket = io(
        process.env.REACT_APP_WEBSOCKETS || 'ws://localhost:3001'
    );

    useEffect(() => {
        if (init.current && socket) {
            init.current = false;

            socket.emit('get-states');
            socket.on('states', (states) => setDevices(states));

            return () => {
                socket.off('states');
            };
        }
    }, [socket]);

    const handleAddTag = (id: string, newTag: string) => {
        setDevices((devices) => {
            return devices.map((device) => {
                if (device.id === id) {
                    device.tags.push(newTag);

                    socket.emit('mqtt-command', {
                        device: device.name,
                        command: `add-tag/${newTag}`,
                    });

                    return device;
                } else {
                    return device;
                }
            });
        });
    };

    const handleRemoveTag = (id: string, tagToRemove: string) => {
        setDevices((devices) => {
            return devices.map((device) => {
                if (device.id === id) {
                    device.tags = device.tags.filter(
                        (tag) => tag !== tagToRemove
                    );

                    socket.emit('mqtt-command', {
                        device: device.name,
                        command: `remove-tag/${tagToRemove}`,
                    });

                    return device;
                } else {
                    return device;
                }
            });
        });
    };

    const handleControl = (selectedDevices: DevicesByTagsType) => {
        setSelectedDevices(selectedDevices);
        history.push('/control');
    };

    const handleCommand = (device: string, command: string) => {
        socket.emit('mqtt-command', { device, command });
    };

    return (
        <>
            <AppContext.Provider value={{ socket, devices, selectedDevices }}>
                <div className="h-100 w-100" style={{ maxWidth: '70rem' }}>
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
                                    <Tags onControl={handleControl} />
                                </Route>

                                <Route path="/devices/:id">
                                    <EditDevice
                                        onAddTag={handleAddTag}
                                        onRemoveTag={handleRemoveTag}
                                    />
                                </Route>

                                <Route path="/devices">
                                    <Devices />
                                </Route>

                                <Route path="/search">
                                    <Search />
                                </Route>

                                <Route path="/control">
                                    <Controls onCommand={handleCommand} />
                                </Route>

                                <Route path="/">
                                    <Redirect to="/commands" />
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
