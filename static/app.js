// Rohrinator - Pipe Assembly Generator UI

// API Base URL
const API_BASE = '/api/v1';

// Three.js globals
let scene, camera, renderer, controls, mesh;
let isWireframe = false;

// Current assembly data
let currentAssembly = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initThreeJS();
    initEventListeners();
    updateFormVisibility();
});

// Initialize Three.js scene
function initThreeJS() {
    const container = document.getElementById('viewer-container');
    const canvas = document.getElementById('viewer');

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f0f23);

    // Camera
    const aspect = container.clientWidth / container.clientHeight;
    camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 10000);
    camera.position.set(500, 400, 600);

    // Renderer
    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 50;
    controls.maxDistance = 3000;

    // Lights
    const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight2.position.set(-1, -1, -1);
    scene.add(directionalLight2);

    // Grid helper
    const gridHelper = new THREE.GridHelper(1000, 20, 0x333333, 0x222222);
    scene.add(gridHelper);

    // Axes helper
    const axesHelper = new THREE.AxesHelper(200);
    scene.add(axesHelper);

    // Handle resize
    window.addEventListener('resize', onWindowResize);

    // Animation loop
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function onWindowResize() {
    const container = document.getElementById('viewer-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

// Initialize event listeners
function initEventListeners() {
    // Assembly type change
    document.getElementById('assembly-type').addEventListener('change', updateFormVisibility);

    // Generate button
    document.getElementById('generate-btn').addEventListener('click', generateAssembly);

    // Viewer controls
    document.getElementById('reset-view').addEventListener('click', resetView);
    document.getElementById('toggle-wireframe').addEventListener('click', toggleWireframe);

    // Reducer position slider
    const reducerSlider = document.getElementById('reducer-position');
    if (reducerSlider) {
        reducerSlider.addEventListener('input', updateReducerPositionLabel);
    }

    // Update reducer visibility based on flange sizes
    document.getElementById('nps-a')?.addEventListener('change', updateReducerVisibility);
    document.getElementById('nps-b')?.addEventListener('change', updateReducerVisibility);

    // Initial visibility check
    updateReducerVisibility();
}

// Update reducer position label
function updateReducerPositionLabel() {
    const slider = document.getElementById('reducer-position');
    const label = document.getElementById('reducer-pos-value');
    if (slider && label) {
        label.textContent = Math.round(slider.value * 100) + '%';
    }
}

// Show/hide reducer position based on flange sizes
function updateReducerVisibility() {
    const npsA = document.getElementById('nps-a')?.value;
    const npsB = document.getElementById('nps-b')?.value;
    const reducerGroup = document.getElementById('reducer-position-group');

    if (reducerGroup) {
        // Show reducer position only if sizes are different
        const needsReducer = npsA && npsB && npsA !== npsB;
        reducerGroup.style.display = needsReducer ? 'block' : 'none';
    }
}

// Update form visibility based on assembly type
function updateFormVisibility() {
    const assemblyType = document.getElementById('assembly-type').value;
    const straightParams = document.getElementById('straight-params');
    const elbowParams = document.getElementById('elbow-params');

    if (assemblyType === 'straight') {
        straightParams.style.display = 'block';
        elbowParams.style.display = 'none';
    } else {
        straightParams.style.display = 'none';
        elbowParams.style.display = 'block';
    }
}

// Generate assembly
async function generateAssembly() {
    const assemblyType = document.getElementById('assembly-type').value;
    const btn = document.getElementById('generate-btn');
    const loading = document.getElementById('loading');
    const status = document.getElementById('status');

    // Disable button and show loading
    btn.disabled = true;
    loading.style.display = 'flex';
    status.textContent = '';
    status.className = 'status';

    try {
        let endpoint, payload;

        const commonParams = {
            project: document.getElementById('project').value,
            designation: document.getElementById('designation').value,
            description: `${assemblyType === 'straight' ? 'Straight' : '90° Elbow'} Pipe Assembly`,
            pressure_class: parseInt(document.getElementById('pressure-class').value),
            nps: document.getElementById('nps').value,
            pipe_schedule: document.getElementById('schedule').value,
            welding_gap: parseFloat(document.getElementById('welding-gap').value)
        };

        if (assemblyType === 'straight') {
            endpoint = `${API_BASE}/assembly/straight`;

            // Get flange sizes
            const npsA = document.getElementById('nps-a')?.value || null;
            const npsB = document.getElementById('nps-b')?.value || null;

            payload = {
                ...commonParams,
                face_to_face: parseFloat(document.getElementById('face-to-face').value),
                nps_a: npsA || null,
                nps_b: npsB || null,
                reducer_position: parseFloat(document.getElementById('reducer-position')?.value || 0.5)
            };
        } else {
            endpoint = `${API_BASE}/assembly/elbow`;
            payload = {
                ...commonParams,
                leg_a_length: parseFloat(document.getElementById('leg-a').value),
                leg_b_length: parseFloat(document.getElementById('leg-b').value),
                bend_radius_factor: document.getElementById('bend-radius').value
            };
        }

        // Call API
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate assembly');
        }

        currentAssembly = await response.json();

        // Update downloads
        updateDownloadLinks(currentAssembly);

        // Load STL into viewer
        await loadSTL(currentAssembly.download_urls.stl);

        // Show BOM
        displayBOM(currentAssembly.metadata);

        status.textContent = 'Assembly generated successfully!';
        status.className = 'status success';

    } catch (error) {
        console.error('Error:', error);
        status.textContent = `Error: ${error.message}`;
        status.className = 'status error';
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
}

// Update download links
function updateDownloadLinks(assembly) {
    const downloads = document.getElementById('downloads');
    downloads.style.display = 'block';

    document.getElementById('download-step').href = assembly.download_urls.step;
    document.getElementById('download-stl').href = assembly.download_urls.stl;
    document.getElementById('download-bom').href = assembly.download_urls.bom;
}

// Load STL file into Three.js viewer
async function loadSTL(url) {
    return new Promise((resolve, reject) => {
        const loader = new THREE.STLLoader();

        loader.load(
            url,
            (geometry) => {
                // Remove existing mesh
                if (mesh) {
                    scene.remove(mesh);
                    mesh.geometry.dispose();
                    mesh.material.dispose();
                }

                // Create material
                const material = new THREE.MeshPhongMaterial({
                    color: 0x4dabf7,
                    specular: 0x111111,
                    shininess: 50,
                    wireframe: isWireframe
                });

                // Create mesh
                mesh = new THREE.Mesh(geometry, material);

                // Center the geometry
                geometry.computeBoundingBox();
                const center = new THREE.Vector3();
                geometry.boundingBox.getCenter(center);
                geometry.translate(-center.x, -center.y, -center.z);

                // Position mesh
                mesh.rotation.x = -Math.PI / 2; // STL typically exports Z-up

                scene.add(mesh);

                // Fit camera to object
                fitCameraToObject();

                resolve();
            },
            undefined,
            (error) => {
                reject(error);
            }
        );
    });
}

// Fit camera to view the entire object
function fitCameraToObject() {
    if (!mesh) return;

    const boundingBox = new THREE.Box3().setFromObject(mesh);
    const size = new THREE.Vector3();
    boundingBox.getSize(size);

    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * (Math.PI / 180);
    const distance = maxDim / (2 * Math.tan(fov / 2)) * 1.5;

    camera.position.set(distance * 0.7, distance * 0.5, distance * 0.7);
    camera.lookAt(0, 0, 0);
    controls.target.set(0, 0, 0);
    controls.update();
}

// Reset view
function resetView() {
    fitCameraToObject();
}

// Toggle wireframe
function toggleWireframe() {
    isWireframe = !isWireframe;
    if (mesh) {
        mesh.material.wireframe = isWireframe;
    }
}

// Display BOM (Bill of Materials)
function displayBOM(metadata) {
    const info = document.getElementById('assembly-info');
    const bomTable = document.getElementById('bom-table');

    info.style.display = 'block';

    if (!metadata || !metadata.components) {
        bomTable.innerHTML = '<p>No component data available</p>';
        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Qty</th>
                    <th>Weight (kg)</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (const comp of metadata.components) {
        html += `
            <tr>
                <td>${comp.item}</td>
                <td>${comp.type}</td>
                <td>${comp.description}</td>
                <td>${comp.quantity}</td>
                <td>${comp.weight_kg || '-'}</td>
            </tr>
        `;
    }

    html += `
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="4"><strong>Total Weight</strong></td>
                    <td><strong>${metadata.total_weight_kg || '-'} kg</strong></td>
                </tr>
            </tfoot>
        </table>
    `;

    bomTable.innerHTML = html;
}
