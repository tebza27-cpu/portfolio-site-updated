
import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";

export default function FundraiserPage() {
  const goal = 90;
  const [donations, setDonations] = useState([]);
  const [name, setName] = useState("");
  const [amount, setAmount] = useState("");

  const total = donations.reduce((sum, d) => sum + d.amount, 0);

  const addDonation = () => {
    if (!name || !amount) return;
    const newDonation = {
      name,
      amount: parseFloat(amount),
      id: Date.now()
    };
    setDonations([newDonation, ...donations]);
    setName("");
    setAmount("");
  };

  const progress = Math.min((total / goal) * 100, 100);

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <Card className="rounded-2xl shadow-lg">
        <CardContent className="p-6 text-center space-y-3">
          <h1 className="text-2xl font-bold">Help Sifiso Stay in School 🎓</h1>
          <p>Raising $90 for BYU Tuition</p>
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className="bg-green-500 h-4"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="font-semibold">${total} raised of ${goal}</p>
          <p className="text-sm">PayPal: tebza27@gmail.com</p>
        </CardContent>
      </Card>

      <Card className="rounded-2xl shadow-md">
        <CardContent className="p-4 space-y-3">
          <h2 className="text-xl font-semibold">Add Contribution</h2>
          <Input
            placeholder="Donor name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Input
            placeholder="Amount ($)"
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          <Button onClick={addDonation}>Add</Button>
        </CardContent>
      </Card>

      <Card className="rounded-2xl shadow-md">
        <CardContent className="p-4 space-y-2">
          <h2 className="text-xl font-semibold">Supporters ❤️</h2>
          {donations.length === 0 && <p>No donations yet</p>}
          {donations.map((d) => (
            <motion.div
              key={d.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-between border-b py-1"
            >
              <span>{d.name}</span>
              <span>${d.amount}</span>
            </motion.div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
