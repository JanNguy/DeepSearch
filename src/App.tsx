import { useState } from "react";
import "./App.css";
import { motion } from "motion/react";

interface UserText {
    pathPP: string;
    message: string;
    type: "ask" | "response";
}

function App() {
  const [open, setOpen] = useState(false);

const conversation: UserText[] = [
    { pathPP: "/assets/ChatGPT-Logo.svg", message: "Hello, how can I help you today?", type: "ask" },
    { pathPP: "/assets/user.png", message: "I'm looking for information about React components.", type: "response"}
];

  return (
    <>
        <div className="flex flex-row h-screen overflow-hidden">
            <motion.nav
            className="h-full bg-neutral-900 order-first overflow-hidden"
            animate={{ width: open ? "20%" : 0 }}
            initial={false}
            transition={{ duration: 0.35, ease: "easeInOut" }}
            >
                <button className="p-4 text-white" onClick={() => setOpen(false)}>←</button>
            </motion.nav>

            <div className="flex-1 h-full bg-neutral-800 flex flex-col relative pt-5">
                <button
                    className={`absolute top-4 left-4 z-10 rounded-md bg-black/60 text-white px-3 py-1 ${open ? 'invisible' : ''}`}
                    onClick={() => setOpen((v) => !v)}
                >
                    {open ? "←" : "→"}
                </button>
                <div className="mb-6 space-y-4 items-start flex flex-col flex-nowrap w-[100%]">
                    {conversation.map((u, index) => (
                        <div key={index} className="flex items-center gap-3 w-[80%] h-auto border-1 border-solid border-white mx-auto p-2">
                            <img src={u.pathPP} alt="profile" className="w-10 h-10 rounded-full object-cover" />
                            <p className="text-white">{u.message}</p>
                        </div>
                    ))}
                </div>
                <div className="flex flex-col mt-auto rounded-3xl bg-black mb-7 m-20 text-white p-5 pl-9">
                    <div className="flex items-center gap-3">
                        <input
                            type="text"
                            name="inputZone"
                            id="input"
                            className="bg-black text-white outline-none flex-1"
                            placeholder="Ask for something"
                        />
                        <div className="rounded-2xl bg-yellow-900 w-10 h-10 ml-auto flex items-center justify-center">
                            <p>→</p>
                        </div>
                     </div>
                </div>
            </div>
      </div>
    </>
  );
}

export default App;
