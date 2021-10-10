import { FormEvent, useContext, useEffect, useState } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { Button, ButtonPrevious, Card, Input, Tag } from '@components';
import { AppContext, IotDevice } from '@models';

export function EditDevice() {
    const appContext = useContext(AppContext);
    const history = useHistory();
    const { urlId } = useParams<{ urlId: string }>();
    const [device, setDevice] = useState<IotDevice>();
    const [tags, setTags] = useState<string[]>([]);
    const [newTag, setNewTag] = useState('');

    useEffect(() => {
        if (urlId && appContext.devices && !device) {
            const device = appContext.devices.find((device) => device.urlId === urlId);

            if (device) {
                setDevice(device);
                setTags(device.tags);
            }
        }
    }, [urlId, appContext.devices]);

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
                <>
                    <div>Name: {device?.id}</div>
                    <div>IP: {device?.ip}</div>
                    <div>Type: {device?.type}</div>
                    <div>State: {device?.state}</div>
                    <div className="flex">
                        {tags.map((tag) => (
                            <Tag
                                key={tag}
                                label={tag}
                                displayClose={true}
                                onRemove={handleRemoveTag}
                            />
                        ))}
                    </div>

                    <form className="flex" onSubmit={handleAddTag}>
                        <Input value={newTag} onChange={(id) => setNewTag(id)} />
                        <Button content="Add" colorClassBackground="bg-blue-700" />
                    </form>
                </>
            </Card>

            <ButtonPrevious onClick={() => history.goBack()} />
        </div>
    );
}
