import React, {useState} from "react";
import "./reaction.css";

type ReactionOption = {
    name: string;
    value: number;
};

type Options = {
    options: ReactionOption[];
    onSelect: (value: number, id: string, comment: boolean) => void;
    itemId: string;
    comment?: boolean;
};

export default function ReactionButton ({ options, onSelect, itemId, comment = true }: Options){
    const [open, setOpen] = useState(false);
    const handleSelect = (value: number) => {
        onSelect(value, itemId, comment); 
        setOpen(false);
    };

    return (
        <div className="dropdown-container">
            <button className="dropdown-button" onClick={() => setOpen(!open)}>
            React
            </button>

            {open && (
            <div className="dropdown-menu">
                {options.map((opt) => (
                <div
                    key={opt.value}
                    className="dropdown-item"
                    onClick={() => handleSelect(opt.value)}
                >
                    {opt.name}
                </div>
                ))}
            </div>
            )}
        </div>
    );
}