'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export function WeaponStats({ data }: { data: any[] }) {
  return (
    <div className="bg-surface-500 border border-secondary-700 rounded-lg p-8">
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2A3542" />
          <XAxis dataKey="weapon" stroke="#8B9BB4" />
          <YAxis stroke="#8B9BB4" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0F1923', border: '1px solid #2A3542' }}
            labelStyle={{ color: '#ECE8E1' }}
          />
          <Legend />
          <Bar dataKey="kills" fill="#4361EE" radius={[8, 8, 0, 0]} />
          <Bar dataKey="accuracy" fill="#69C9D0" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-6">
        <h3 className="font-semibold mb-4">Breakdown</h3>
        <div className="space-y-3">
          {data.map((weapon, idx) => (
            <div key={idx} className="flex justify-between items-center p-3 bg-secondary-600/50 rounded">
              <div>
                <p className="font-semibold">{weapon.weapon}</p>
                <p className="text-secondary-400 text-sm">{weapon.kills} kills</p>
              </div>
              <div className="text-right">
                <p className="font-semibold">{weapon.accuracy.toFixed(1)}%</p>
                <p className="text-secondary-400 text-sm">accuracy</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
