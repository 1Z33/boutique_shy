"use client";

import { Canvas } from "@react-three/fiber";
import { Environment, ContactShadows, Float, OrbitControls, Text } from "@react-three/drei";
import { Suspense } from "react";
import * as THREE from "three";

type Props = { onSelectProduct: (id: number) => void };

function Plinth({ position, scale = 1 }: { position: [number, number, number]; scale?: number }) {
  return <mesh position={position} scale={[scale, 1, scale]} castShadow receiveShadow><cylinderGeometry args={[0.52, 0.58, 0.12, 48]} /><meshStandardMaterial color="#d8c8b5" roughness={0.78} /></mesh>;
}

function DressDisplay({ position, color, productId, onSelect }: { position: [number, number, number]; color: string; productId: number; onSelect: (id: number) => void }) {
  return (
    <group position={position} onClick={(e) => { e.stopPropagation(); onSelect(productId); }}>
      <mesh position={[0, 1.42, 0]} castShadow><capsuleGeometry args={[0.12, 0.42, 5, 12]} /><meshStandardMaterial color="#c7ad91" roughness={0.65} /></mesh>
      <mesh position={[0, 1.02, 0]} castShadow><coneGeometry args={[0.43, 0.92, 4]} /><meshStandardMaterial color={color} roughness={0.82} side={THREE.DoubleSide} /></mesh>
      <mesh position={[0, 1.47, 0]}><torusGeometry args={[0.23, 0.025, 8, 32]} /><meshStandardMaterial color="#a88b65" metalness={0.55} roughness={0.35} /></mesh>
      <Plinth position={[0, 0.06, 0]} scale={0.8} />
    </group>
  );
}

function ShoeDisplay({ position, onSelect }: { position: [number, number, number]; onSelect: (id: number) => void }) {
  return (
    <group position={position} onClick={(e) => { e.stopPropagation(); onSelect(2); }}>
      <mesh position={[0, 0.34, 0]} rotation={[0, 0, -0.08]} castShadow><boxGeometry args={[0.62, 0.16, 0.28]} /><meshStandardMaterial color="#8b6555" roughness={0.45} /></mesh>
      <mesh position={[0.2, 0.23, -0.02]}><boxGeometry args={[0.12, 0.18, 0.12]} /><meshStandardMaterial color="#a88b65" metalness={0.5} /></mesh>
      <mesh position={[0, 0.12, 0]}><boxGeometry args={[0.7, 0.07, 0.32]} /><meshStandardMaterial color="#4b3c33" roughness={0.65} /></mesh>
    </group>
  );
}

function Rack({ position, onSelect }: { position: [number, number, number]; onSelect: (id: number) => void }) {
  return (
    <group position={position}>
      <mesh position={[0, 1.7, 0]}><boxGeometry args={[2.6, 0.055, 0.055]} /><meshStandardMaterial color="#9d805b" metalness={0.72} roughness={0.28} /></mesh>
      {[-0.95, -0.48, 0, 0.48, 0.95].map((x, i) => <group key={x} position={[x, 0, 0]} onClick={(e) => { e.stopPropagation(); onSelect(1); }}>
        <mesh position={[0, 1.42, 0]}><torusGeometry args={[0.13, 0.012, 6, 24, Math.PI]} rotation={[0, 0, Math.PI]} /><meshStandardMaterial color="#b49a78" metalness={0.7} /></mesh>
        <mesh position={[0, 1.05, 0]} castShadow><coneGeometry args={[0.25, 0.82, 4]} /><meshStandardMaterial color={["#c6b7a4", "#6c5148", "#d5c7b6", "#8a7767", "#b8a18b"][i]} roughness={0.9} /></mesh>
      </group>)}
      <mesh position={[-1.28, 0.84, 0]}><cylinderGeometry args={[0.035, 0.035, 1.7, 12]} /><meshStandardMaterial color="#9d805b" metalness={0.7} /></mesh>
      <mesh position={[1.28, 0.84, 0]}><cylinderGeometry args={[0.035, 0.035, 1.7, 12]} /><meshStandardMaterial color="#9d805b" metalness={0.7} /></mesh>
      <mesh position={[0, 0.08, 0]}><boxGeometry args={[2.75, 0.1, 0.42]} /><meshStandardMaterial color="#4b392e" roughness={0.65} /></mesh>
    </group>
  );
}

function Room({ onSelect }: Props) {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.04, 0]} receiveShadow><planeGeometry args={[24, 24]} /><meshStandardMaterial color="#cfc0ad" roughness={0.86} /></mesh>
      <mesh position={[0, 2.7, -5.4]} receiveShadow><boxGeometry args={[15, 5.5, 0.18]} /><meshStandardMaterial color="#e9e0d4" roughness={0.92} /></mesh>
      <mesh position={[-7.3, 2.7, 0]}><boxGeometry args={[0.18, 5.5, 11]} /><meshStandardMaterial color="#ddd0c0" roughness={0.9} /></mesh>
      <mesh position={[7.3, 2.7, 0]}><boxGeometry args={[0.18, 5.5, 11]} /><meshStandardMaterial color="#ddd0c0" roughness={0.9} /></mesh>
      <mesh position={[0, 5.5, 0]}><boxGeometry args={[14.6, 0.12, 11]} /><meshStandardMaterial color="#e6ddd1" roughness={0.9} /></mesh>
      <mesh position={[0, 3.65, -5.28]}><boxGeometry args={[4.6, 0.018, 0.02]} /><meshStandardMaterial color="#a78c68" metalness={0.55} /></mesh>
      <Text position={[0, 4.1, -5.25]} fontSize={0.48} color="#51453b" anchorX="center" letterSpacing={0.12}>SHY BOUTIQUE</Text>
      <Text position={[0, 3.76, -5.25]} fontSize={0.105} color="#8c7967" anchorX="center" letterSpacing={0.24}>MAISON DE MODE</Text>
      <Rack position={[-3.9, 0, -2.7]} onSelect={onSelect} />
      <Rack position={[3.9, 0, -2.7]} onSelect={onSelect} />
      <DressDisplay position={[-2.4, 0, 0.2]} color="#9c796d" productId={1} onSelect={onSelect} />
      <DressDisplay position={[0, 0, -0.3]} color="#d2c2ad" productId={3} onSelect={onSelect} />
      <ShoeDisplay position={[2.5, 0, 0.2]} onSelect={onSelect} />
      <mesh position={[0, 1.35, -4.85]}><boxGeometry args={[2.5, 0.035, 0.45]} /><meshStandardMaterial color="#6a5040" roughness={0.55} /></mesh>
      <mesh position={[-6.2, 2.7, -1.2]}><boxGeometry args={[0.05, 3.4, 2.8]} /><meshStandardMaterial color="#8f7966" metalness={0.25} roughness={0.22} /></mesh>
      <mesh position={[6.2, 2.7, -1.2]}><boxGeometry args={[0.05, 3.4, 2.8]} /><meshStandardMaterial color="#8f7966" metalness={0.25} roughness={0.22} /></mesh>
      <mesh position={[0, 0.12, 2.9]}><boxGeometry args={[3.3, 0.24, 1.25]} /><meshStandardMaterial color="#5a4334" roughness={0.55} /></mesh>
      <mesh position={[0, 0.3, 2.9]}><boxGeometry args={[3.15, 0.12, 1.12]} /><meshStandardMaterial color="#b79d7e" roughness={0.78} /></mesh>
    </group>
  );
}

export default function BoutiqueScene({ onSelectProduct }: Props) {
  return (
    <div className="scene-canvas">
      <Canvas shadows dpr={[1, 1.5]} camera={{ position: [9, 6.2, 10], fov: 43 }}>
        <color attach="background" args={["#c8b9a7"]} />
        <fog attach="fog" args={["#c8b9a7", 13, 26]} />
        <ambientLight intensity={1.1} />
        <directionalLight position={[4, 9, 5]} intensity={2.1} castShadow shadow-mapSize={[1024, 1024]} />
        <spotLight position={[-5, 6, -3]} intensity={65} angle={0.48} penumbra={0.8} color="#f4dfc3" />
        <Suspense fallback={null}>
          <Room onSelect={onSelectProduct} />
          <Environment preset="apartment" />
          <ContactShadows position={[0, 0, 0]} opacity={0.3} scale={18} blur={2.5} far={5} />
        </Suspense>
        <OrbitControls target={[0, 1.3, -0.5]} minDistance={6} maxDistance={17} minPolarAngle={0.45} maxPolarAngle={1.48} enablePan={false} />
      </Canvas>
    </div>
  );
}