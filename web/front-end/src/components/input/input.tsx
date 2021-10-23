import { ChangeEvent, useEffect, useState } from 'react';
import styles from './input.module.css';

type InputSize = 'tiny' | 'small' | 'medium' | 'regular' | 'large' | 'full';
type InputType = 'text' | 'number' | 'email' | 'password' | 'date';

type Props = {
    value?: string;
    size?: InputSize;
    type?: InputType;
    placeholder?: string;
    minLength?: number;
    maxLength?: number;
    onChange?: (value: string) => void;
};

export function Input(props: Props) {
    const dummyCallback = () => true;
    const {
        value = '',
        size = 'regular',
        type = 'text',
        placeholder = '',
        minLength = -1,
        maxLength = -1,
        onChange = dummyCallback,
    } = props;
    const [width, setWidth] = useState({});
    const [inputValue, setInputValue] = useState('');

    useEffect(() => {
        setInputValue(value);
    }, [value]);

    useEffect(() => {
        switch (size) {
            case 'tiny':
                setWidth({ width: '3rem' });
                break;
            case 'small':
                setWidth({ width: '5rem' });
                break;
            case 'medium':
                setWidth({ width: '9rem' });
                break;
            case 'regular':
                setWidth({ width: '14rem' });
                break;
            case 'large':
                setWidth({ width: '33rem' });
                break;
            case 'full':
                setWidth({ width: '100%' });
                break;
        }
    }, [size]);

    const id =
        'input' + new Date().getTime().toString() + Math.floor(Math.random() * 100).toString();

    const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
        onChange(event.currentTarget.value);
        setInputValue(event.currentTarget.value);
    };

    return (
        <div className={`${styles.component}`}>
            <input
                id={id}
                type={type}
                minLength={minLength}
                maxLength={maxLength}
                value={inputValue}
                placeholder={placeholder}
                onChange={handleChange}
                className={`text-white bg-gray-500 px-3 py-2 border-2 border-transparent
                    focus:border-yellow-500 rounded-full outline-none`}
                style={width}
            />
        </div>
    );
}
