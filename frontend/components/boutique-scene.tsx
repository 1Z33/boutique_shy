"use client";

import { Canvas } from "@react-three/fiber";
import { ContactShadows, Environment, OrbitControls, Text } from "@react-three/drei";
import { Suspense } from "react";
import * as THREE from "three";

type Props = { onSelectProduct: (id: number) => void };
type Point = [number, number, number];

const brass = "#a88b63";
const wood = "#49382e";

function Material({ color, metalness = 0, roughness = 0.72 }: { color: string; metalness?: number; roughness?: number }) {
  return <meshStandardMaterial color={color} metalness={metalness} roughness={roughness} />;
}

function Floor() {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.08, 0]} receiveShadow>
        <planeGeometry args={[22, 22]} /><Material color="#cbbda9" roughness={0.42} />
      </mesh>
      {Array.from({ length: 13 }, (_, i) => (
        <mesh key={`tile-x-${i}`} rotation={[-Math.PI / 2, 0, 0]} position={[-6 + i, -0.069, 0]}>
          <planeGeometry args={[0.009, 10.5]} /><Material color="#b6a58f" />
        </mesh>
      ))}
      {Array.from({ length: 10 }, (_, i) => (
        <mesh key={`tile-z-${i}`} rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.068, -4.5 + i]}>
          <planeGeometry args={[13, 0.009]} /><Material color="#b6a58f" />
        </mesh>
      ))}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.061, 1.1]}>
        <circleGeometry args={[2.15, 64]} /><meshStandardMaterial color="#d9cbbc" roughness={0.48} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.055, 1.1]}>
        <ringGeometry args={[2.12, 2.16, 64]} /><Material color={brass} metalness={0.5} roughness={0.35} />
      </mesh>
    </group>
  );
}

function WallPanel({ x, y = 2.65, z = -5.32 }: { x: number; y?: number; z?: number }) {
  return (
    <group position={[x, y, z]}>
      <mesh><boxGeometry args={[2.45, 3.65, 0.12]} /><Material color="#ded2c2" /></mesh>
      <mesh position={[0, 0, 0.071]}><boxGeometry args={[2.28, 3.48, 0.018]} /><Material color="#e9e0d4" /></mesh>
      <mesh position={[0, 0, 0.09]}><boxGeometry args={[2.12, 3.31, 0.012]} /><Material color="#d6c7b5" /></mesh>
      <mesh position={[0, 0, 0.105]}><boxGeometry args={[2.02, 3.2, 0.014]} /><Material color="#e8ded1" /></mesh>
    </group>
  );
}

function BrandWall() {
  return (
    <group position={[0, 0, -5.18]}>
      <mesh position={[0, 2.7, 0]}><boxGeometry args={[15, 5.5, 0.2]} /><Material color="#e7ded2" /></mesh>
      <mesh position={[0, 2.72, 0.12]}><boxGeometry args={[5.25, 4.1, 0.025]} /><Material color="#d4c3af" /></mesh>
      <mesh position={[0, 2.72, 0.145]}><boxGeometry args={[5.03, 3.88, 0.025]} /><Material color="#eee7dd" /></mesh>
      <mesh position={[0, 2.72, 0.17]}><boxGeometry args={[4.82, 3.68, 0.025]} /><Material color="#e5d9ca" /></mesh>
      <Text position={[0, 3.08, 0.21]} fontSize={0.48} color="#514438" anchorX="center" letterSpacing={0.13}>SHY BOUTIQUE</Text>
      <mesh position={[0, 2.69, 0.215]}><boxGeometry args={[2.7, 0.012, 0.012]} /><Material color={brass} metalness={0.7} roughness={0.3} /></mesh>
      <Text position={[0, 2.4, 0.21]} fontSize={0.105} color="#8c7967" anchorX="center" letterSpacing={0.27}>MAISON DE MODE</Text>
      <Text position={[0, 1.7, 0.21]} fontSize={0.095} color="#9a8876" anchorX="center" letterSpacing={0.12}>L'ART DE SE SENTIR SOI</Text>
      <WallPanel x={-4.45} />
      <WallPanel x={4.45} />
    </group>
  );
}

function Arch({ position, scale = 1 }: { position: Point; scale?: number }) {
  return (
    <group position={position} scale={scale}>
      <mesh position={[-1.28, 1.15, 0]}><boxGeometry args={[0.12, 2.3, 0.12]} /><Material color={brass} metalness={0.65} roughness={0.3} /></mesh>
      <mesh position={[1.28, 1.15, 0]}><boxGeometry args={[0.12, 2.3, 0.12]} /><Material color={brass} metalness={0.65} roughness={0.3} /></mesh>
      <mesh position={[0, 2.3, 0]}><torusGeometry args={[1.28, 0.06, 12, 64, Math.PI]} /><Material color={brass} metalness={0.65} roughness={0.3} /></mesh>
    </group>
  );
}

function Garment({ x, color, onSelect }: { x: number; color: string; onSelect: () => void }) {
  return (
    <group position={[x, 0, 0]} onClick={(e) => { e.stopPropagation(); onSelect(); }}>
      <mesh position={[0, 1.48, 0]}><torusGeometry args={[0.12, 0.012, 6, 24, Math.PI]} rotation={[0, 0, Math.PI]} /><Material color={brass} metalness={0.75} roughness={0.28} /></mesh>
      <mesh position={[0, 1.05, 0]} castShadow>
        <coneGeometry args={[0.23, 0.86, 4]} /><meshStandardMaterial color={color} roughness={0.92} side={THREE.DoubleSide} />
      </mesh>
      <mesh position={[0, 1.42, 0]}><capsuleGeometry args={[0.095, 0.16, 4, 8]} /><Material color={color} /></mesh>
    </group>
  );
}

function Rack({ position, onSelect }: { position: Point; onSelect: (id: number) => void }) {
  const colors = ["#c9b8a5", "#72564c", "#e4d9c9", "#998271", "#b9a18a", "#6c6258"];
  return (
    <group position={position}>
      <mesh position={[0, 1.76, 0]}><cylinderGeometry args={[0.035, 0.035, 3.05, 12]} rotation={[0, 0, Math.PI / 2]} /><Material color={brass} metalness={0.8} roughness={0.28} /></mesh>
      {colors.map((color, i) => <Garment key={i} x={-1.15 + i * 0.46} color={color} onSelect={() => onSelect(1)} />)}
      {[-1.52, 1.52].map((x) => (
        <group key={x} position={[x, 0, 0]}>
          <mesh position={[0, 0.88, 0]}><cylinderGeometry args={[0.035, 0.045, 1.75, 12]} /><Material color={brass} metalness={0.78} roughness={0.3} /></mesh>
          <mesh position={[0, 0.08, 0]}><cylinderGeometry args={[0.1, 0.1, 0.08, 20]} /><Material color={wood} /></mesh>
        </group>
      ))}
      <mesh position={[0, 0.08, 0]}><boxGeometry args={[3.3, 0.12, 0.46]} /><Material color={wood} /></mesh>
      <mesh position={[0, 0.15, 0]}><boxGeometry args={[3.25, 0.025, 0.43]} /><Material color="#a98c69" metalness={0.3} roughness={0.4} /></mesh>
    </group>
  );
}

function Mannequin({ position, color, onSelect, productId }: { position: Point; color: string; onSelect: (id: number) => void; productId: number }) {
  return (
    <group position={position} onClick={(e) => { e.stopPropagation(); onSelect(productId); }}>
      <mesh position={[0, 1.8, 0]} castShadow><sphereGeometry args={[0.16, 24, 24]} /><Material color="#b99d81" roughness={0.55} /></mesh>
      <mesh position={[0, 1.47, 0]} castShadow><capsuleGeometry args={[0.2, 0.42, 6, 16]} /><Material color="#b99d81" roughness={0.6} /></mesh>
      <mesh position={[0, 0.91, 0]} castShadow><coneGeometry args={[0.43, 0.78, 32]} /><meshStandardMaterial color={color} roughness={0.82} side={THREE.DoubleSide} /></mesh>
      <mesh position={[0, 1.13, 0]}><torusGeometry args={[0.205, 0.018, 8, 32]} /><Material color={brass} metalness={0.7} roughness={0.28} /></mesh>
      <mesh position={[0, 0.47, 0]}><cylinderGeometry args={[0.035, 0.035, 0.22, 12]} /><Material color={brass} metalness={0.7} /></mesh>
      <mesh position={[0, 0.32, 0]}><cylinderGeometry args={[0.28, 0.34, 0.1, 48]} /><Material color="#e0d3c2" roughness={0.48} /></mesh>
      <mesh position={[0, 0.26, 0]}><cylinderGeometry args={[0.23, 0.23, 0.025, 48]} /><Material color={brass} metalness={0.65} roughness={0.32} /></mesh>
    </group>
  );
}

function ShoePair({ position, onSelect }: { position: Point; onSelect: (id: number) => void }) {
  return (
    <group position={position} onClick={(e) => { e.stopPropagation(); onSelect(2); }}>
      {[-0.24, 0.24].map((x) => (
        <group key={x} position={[x, 0, 0]} rotation={[0, 0, x > 0 ? 0.12 : -0.12]}>
          <mesh position={[0, 0.18, 0]} castShadow><boxGeometry args={[0.25, 0.12, 0.52]} /><Material color="#79594c" roughness={0.36} /></mesh>
          <mesh position={[0, 0.1, -0.17]}><boxGeometry args={[0.1, 0.16, 0.11]} /><Material color={brass} metalness={0.6} roughness={0.3} /></mesh>
          <mesh position={[0, 0.1, 0.04]}><boxGeometry args={[0.27, 0.045, 0.56]} /><Material color="#392f29" roughness={0.5} /></mesh>
        </group>
      ))}
      <mesh position={[0, 0.025, 0]}><boxGeometry args={[1.05, 0.06, 0.8]} /><Material color="#d7c7b5" roughness={0.55} /></mesh>
    </group>
  );
}

function Handbag({ position, onSelect }: { position: Point; onSelect: (id: number) => void }) {
  return (
    <group position={position} onClick={(e) => { e.stopPropagation(); onSelect(3); }}>
      <mesh position={[0, 0.38, 0]} castShadow><boxGeometry args={[0.65, 0.52, 0.24]} /><Material color="#8a6654" roughness={0.42} /></mesh>
      <mesh position={[0, 0.69, 0]}><torusGeometry args={[0.22, 0.025, 8, 32, Math.PI]} rotation={[0, 0, Math.PI]} /><Material color={brass} metalness={0.7} roughness={0.28} /></mesh>
      <mesh position={[0, 0.4, 0.13]}><boxGeometry args={[0.12, 0.07, 0.015]} /><Material color={brass} metalness={0.75} roughness={0.24} /></mesh>
    </group>
  );
}

function Pedestal({ position, children }: { position: Point; children: React.ReactNode }) {
  return (
    <group position={position}>
      <mesh position={[0, 0.5, 0]} castShadow receiveShadow><cylinderGeometry args={[0.54, 0.58, 1, 48]} /><Material color="#e5d9ca" roughness={0.55} /></mesh>
      <mesh position={[0, 1.02, 0]}><cylinderGeometry args={[0.55, 0.55, 0.045, 48]} /><Material color={brass} metalness={0.62} roughness={0.3} /></mesh>
      {children}
    </group>
  );
}

function Plant({ position }: { position: Point }) {
  return (
    <group position={position}>
      <mesh position={[0, 0.35, 0]}><cylinderGeometry args={[0.25, 0.18, 0.65, 24]} /><Material color="#8e7460" roughness={0.65} /></mesh>
      <mesh position={[0, 0.68, 0]}><cylinderGeometry args={[0.2, 0.2, 0.06, 24]} /><Material color="#4a392e" /></mesh>
      {Array.from({ length: 7 }, (_, i) => {
        const angle = (i / 7) * Math.PI * 2;
        return <mesh key={i} position={[Math.cos(angle) * 0.18, 1.18 + (i % 3) * 0.1, Math.sin(angle) * 0.18]} rotation={[0.3, angle, -0.35]}>
          <coneGeometry args={[0.13, 0.82, 7]} /><Material color={i % 2 ? "#53634c" : "#68765a"} roughness={0.9} />
        </mesh>;
      })}
      <mesh position={[0, 1.02, 0]}><cylinderGeometry args={[0.035, 0.035, 0.7, 8]} /><Material color="#66523e" /></mesh>
    </group>
  );
}

function CeilingLights() {
  return (
    <group>
      <mesh position={[0, 5.35, 0]}><boxGeometry args={[10, 0.08, 0.12]} /><Material color={brass} metalness={0.75} roughness={0.3} /></mesh>
      {[-4, -2, 0, 2, 4].map((x) => (
        <group key={x} position={[x, 5.12, 0]}>
          <mesh><cylinderGeometry args={[0.16, 0.12, 0.28, 24]} /><Material color="#4b4035" metalness={0.45} roughness={0.35} /></mesh>
          <mesh position={[0, -0.16, 0]}><cylinderGeometry args={[0.1, 0.14, 0.035, 24]} /><meshStandardMaterial color="#f5e6c9" emissive="#f5d9a9" emissiveIntensity={0.65} /></mesh>
          <spotLight position={[0, -0.2, 0]} intensity={18} angle={0.55} penumbra={0.85} color="#ffedcf" distance={8} />
        </group>
      ))}
    </group>
  );
}

function Room({ onSelect }: Props) {
  return (
    <group>
      <Floor />
      <BrandWall />
      <mesh position={[-7.35, 2.7, 0]}><boxGeometry args={[0.18, 5.5, 11]} /><Material color="#d9cbbb" /></mesh>
      <mesh position={[7.35, 2.7, 0]}><boxGeometry args={[0.18, 5.5, 11]} /><Material color="#d9cbbb" /></mesh>
      <mesh position={[0, 5.48, 0]}><boxGeometry args={[14.7, 0.12, 11]} /><Material color="#e8dfd4" /></mesh>
      <Arch position={[-6.9, 0, -1.6]} scale={0.9} />
      <Arch position={[6.9, 0, -1.6]} scale={0.9} />
      <Rack position={[-4.1, 0, -2.5]} onSelect={onSelect} />
      <Rack position={[4.1, 0, -2.5]} onSelect={onSelect} />
      <Pedestal position={[-2.3, 0, 0.1]}><Mannequin position={[0, 1.05, 0]} color="#9b796d" productId={1} onSelect={onSelect} /></Pedestal>
      <Pedestal position={[0, 0, -0.6]}><Mannequin position={[0, 1.05, 0]} color="#d1bda6" productId={3} onSelect={onSelect} /></Pedestal>
      <Pedestal position={[2.35, 0, 0.15]}><ShoePair position={[0, 1.05, 0]} onSelect={onSelect} /></Pedestal>
      <Pedestal position={[4.8, 0, 0.2]}><Handbag position={[0, 1.05, 0]} onSelect={onSelect} /></Pedestal>
      <Plant position={[-6.1, 0, 2.2]} />
      <Plant position={[6.1, 0, 2.2]} />
      <mesh position={[0, 0.18, 3.55]}><boxGeometry args={[3.8, 0.36, 1.3]} /><Material color={wood} roughness={0.48} /></mesh>
      <mesh position={[0, 0.39, 3.55]}><boxGeometry args={[3.68, 0.1, 1.2]} /><Material color="#b9a080" roughness={0.55} /></mesh>
      <mesh position={[0, 0.45, 3.55]}><boxGeometry args={[3.45, 0.025, 1.05]} /><Material color="#e3d6c5" roughness={0.5} /></mesh>
      <Text position={[0, 0.53, 3.55]} rotation={[-Math.PI / 2, 0, 0]} fontSize={0.15} color="#655443" anchorX="center" letterSpacing={0.15}>WELCOME TO SHY</Text>
      <CeilingLights />
    </group>
  );
}

export default function BoutiqueScene({ onSelectProduct }: Props) {
  return (
    <div className="scene-canvas">
      <Canvas shadows dpr={[1, 1.5]} camera={{ position: [10, 7.2, 11], fov: 42 }}>
        <color attach="background" args={["#cbbda9"]} />
        <fog attach="fog" args={["#cbbda9", 15, 29]} />
        <ambientLight intensity={0.72} />
        <hemisphereLight args={["#fff1df", "#7d6a58", 0.8]} />
        <directionalLight position={[4, 9, 5]} intensity={2.2} castShadow shadow-mapSize={[2048, 2048]} />
        <spotLight position={[-5, 6, -3]} intensity={32} angle={0.48} penumbra={0.8} color="#f4dfc3" castShadow />
        <Suspense fallback={null}>
          <Room onSelect={onSelectProduct} />
          <Environment preset="apartment" />
          <ContactShadows position={[0, -0.035, 0]} opacity={0.32} scale={19} blur={2.5} far={5} />
        </Suspense>
        <OrbitControls target={[0, 1.45, -0.2]} minDistance={7} maxDistance={18} minPolarAngle={0.48} maxPolarAngle={1.45} enablePan={false} />
      </Canvas>
    </div>
  );
}
