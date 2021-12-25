import { FormEvent, useContext, useEffect, useState } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { Button, ButtonBack, Card, Input, Tag } from '@components';
import { AppContext, IotDevice } from '@models';

export function EditDevice() {
    const appContext = useContext(AppContext);
    const history = useHistory();
    const { urlId } = useParams<{ urlId: string }>();
    const [device, setDevice] = useState<IotDevice>();
    const [tags, setTags] = useState<string[]>([]);
    const [newTag, setNewTag] = useState('');

    useEffect(() => {
        if (urlId && appContext.store.devices && !device) {
            const device = appContext.store.devices.find((device) => device.urlId === urlId);

            if (device) {
                setDevice(device);
                setTags(device.tags);
            }
        }
    }, [urlId, appContext.store.devices, device]);

    const handleRemoveTag = (tagToRemove: string) => {
        if (device) {
            setTags((tags) => {
                const newTags = tags.filter((tag) => tag !== tagToRemove);
                device.tags = newTags;
                return newTags;
            });

            appContext.socket?.emit('mqtt-command', {
                device: device.id,
                command: `remove-tag/${tagToRemove}`,
            });
        }
    };

    const handleAddTag = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        // Add the new tag if not yet added previously
        if (device?.tags.findIndex((tag) => tag === newTag) === -1) {
            setTags((tags) => {
                const newTags = [...tags, newTag];
                device.tags = newTags;

                return newTags;
            });

            appContext.socket?.emit('mqtt-command', {
                device: device.id,
                command: `add-tag/${newTag}`,
            });
        }

        setNewTag('');
    };

    return (
        <div className="m-5">
            <Card>
                <div className="m-2">
                    <div className="flex">
                        <div className="flex text-2xl">
                            <div>{device?.type}</div>
                            <div className="mx-4">{device?.netId}</div>
                            <div className="mx-2 text-gray-400">{device?.state}</div>
                        </div>
                    </div>

                    <div className="inline-flex mt-2 py-1 px-2 rounded-md bg-gray-800 text-lg">
                        <div className="mr-3">{device?.ip}</div>
                    </div>

                    <div className="flex flex-wrap my-5">
                        {tags.map((tag) => (
                            <Tag
                                key={tag}
                                label={tag}
                                displayClose={true}
                                onRemove={handleRemoveTag}
                            />
                        ))}
                    </div>

                    <div className="flex justify-between">
                        <form className="flex" onSubmit={handleAddTag}>
                            <Input value={newTag} onChange={(id) => setNewTag(id)} />

                            <div className="mr-3"></div>

                            <Button content="Add" colorClassBackground="bg-blue-700" />
                        </form>
                    </div>
                </div>
            </Card>

            <div className="flex justify-end mt-5">
                <ButtonBack onClick={() => history.goBack()} />
            </div>
        </div>
    );
}
