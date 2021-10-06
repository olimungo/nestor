import { FormEvent, useContext, useEffect, useState } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { Button, ButtonPrevious, Card, Input, Tag } from '@components';
import { AppContext, IotDevice } from '@models';

type Props = {
    onAddTag: (id: string, tag: string) => void;
    onRemoveTag: (id: string, tag: string) => void;
};

export function EditDevice(props: Props) {
    const dummyCallback = () => true;
    const { onAddTag = dummyCallback, onRemoveTag = dummyCallback } = props;
    const appContext = useContext(AppContext);
    const history = useHistory();
    const { id } = useParams<{ id: string }>();
    const [device, setDevice] = useState<IotDevice>();
    const [tags, setTags] = useState<string[]>([]);
    const [newTag, setNewTag] = useState('');

    useEffect(() => {
        if (id && appContext.devices) {
            const device = appContext.devices.find(
                (device) => device.id === id
            );

            if (device) {
                setDevice(device);
                setTags(device.tags);
            }
        }
    }, [id, appContext.devices]);

    const handleRemove = (tagToRemove: string) => {
        if (device) {
            onRemoveTag(device.id, tagToRemove);
        }
    };

    const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        // Add the new tag if not yet added previously
        if (tags.findIndex((tag) => tag === newTag) === -1) {
            if (device) {
                onAddTag(device.id, newTag);
            }
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
                                onRemove={handleRemove}
                            />
                        ))}
                    </div>

                    <form className="flex" onSubmit={handleSubmit}>
                        <Input
                            value={newTag}
                            onChange={(id) => setNewTag(id)}
                        />
                        <Button
                            content="Add"
                            colorClassBackground="bg-blue-700"
                        />
                    </form>
                </>
            </Card>

            <ButtonPrevious onClick={() => history.goBack()} />
        </div>
    );
}
