document.addEventListener('DOMContentLoaded', function() {
    console.log('Location dropdown script loaded');

    const regionDropdown = document.getElementById('id_region');
    const provinceDropdown = document.getElementById('id_province');
    const cityDropdown = document.getElementById('id_city_or_municipality');
    const barangayDropdown = document.getElementById('id_barangay');

    if (!regionDropdown || !provinceDropdown || !cityDropdown || !barangayDropdown) {
        console.error('One or more dropdowns not found!');
        return;
    }

    // Initially disable dependent dropdowns
    provinceDropdown.disabled = true;
    cityDropdown.disabled = true;
    barangayDropdown.disabled = true;

    let regionsLoaded = false;
    const cachedData = {
        provinces: {},
        cities: {},
        barangays: {}
    };

    function populateDropdown(dropdown, data, selectedValue = null, valueField='id', textField='name') {
        dropdown.innerHTML = '<option value="">Select</option>';
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item[valueField];
            option.textContent = item[textField];
            if (selectedValue && item[valueField] == selectedValue) {
                option.selected = true;
            }
            dropdown.appendChild(option);
        });
    }

    // Store initial values for edit mode
    const initialValues = {
        region: regionDropdown.value,
        province: provinceDropdown.value,
        city: cityDropdown.value,
        barangay: barangayDropdown.value
    };

    const isEditMode = initialValues.region || initialValues.province || initialValues.city || initialValues.barangay;

    // Lazy load regions on focus
    regionDropdown.addEventListener('focus', function loadRegions() {
        if (regionsLoaded) return;

        const currentValue = regionDropdown.value;
        regionDropdown.innerHTML = '<option value="">Loading...</option>';

        fetch('/locations/regions/')
            .then(res => res.json())
            .then(data => {
                populateDropdown(regionDropdown, data, currentValue);
                regionsLoaded = true;
            })
            .catch(error => {
                console.error('Error fetching regions:', error);
                regionDropdown.innerHTML = '<option value="">Error loading</option>';
            });
    });

    // Region change
    regionDropdown.addEventListener('change', function() {
        const regionId = regionDropdown.value;

        // Reset dependent dropdowns
        provinceDropdown.innerHTML = '<option value="">Select Province</option>';
        provinceDropdown.disabled = !regionId;
        cityDropdown.innerHTML = '<option value="">Select City/Municipality</option>';
        cityDropdown.disabled = true;
        barangayDropdown.innerHTML = '<option value="">Select Barangay</option>';
        barangayDropdown.disabled = true;

        if (!regionId) return;

        // Fetch provinces only if not cached
        if (cachedData.provinces[regionId]) {
            populateDropdown(provinceDropdown, cachedData.provinces[regionId]);
            return;
        }

        provinceDropdown.innerHTML = '<option value="">Loading...</option>';

        fetch(`/locations/provinces/${regionId}/`)
            .then(res => res.json())
            .then(data => {
                cachedData.provinces[regionId] = data;
                populateDropdown(provinceDropdown, data);
            })
            .catch(error => {
                console.error('Error fetching provinces:', error);
                provinceDropdown.innerHTML = '<option value="">Error loading</option>';
            });
    });

    // Province change
    provinceDropdown.addEventListener('change', function() {
        const provinceId = provinceDropdown.value;

        cityDropdown.innerHTML = '<option value="">Select City/Municipality</option>';
        cityDropdown.disabled = !provinceId;
        barangayDropdown.innerHTML = '<option value="">Select Barangay</option>';
        barangayDropdown.disabled = true;

        if (!provinceId) return;

        if (cachedData.cities[provinceId]) {
            populateDropdown(cityDropdown, cachedData.cities[provinceId]);
            return;
        }

        cityDropdown.innerHTML = '<option value="">Loading...</option>';

        fetch(`/locations/cities/${provinceId}/`)
            .then(res => res.json())
            .then(data => {
                cachedData.cities[provinceId] = data;
                populateDropdown(cityDropdown, data);
            })
            .catch(error => {
                console.error('Error fetching cities:', error);
                cityDropdown.innerHTML = '<option value="">Error loading</option>';
            });
    });

    // City change
    cityDropdown.addEventListener('change', function() {
        const cityId = cityDropdown.value;

        barangayDropdown.innerHTML = '<option value="">Select Barangay</option>';
        barangayDropdown.disabled = !cityId;

        if (!cityId) return;

        if (cachedData.barangays[cityId]) {
            populateDropdown(barangayDropdown, cachedData.barangays[cityId]);
            return;
        }

        barangayDropdown.innerHTML = '<option value="">Loading...</option>';

        fetch(`/locations/barangays/${cityId}/`)
            .then(res => res.json())
            .then(data => {
                cachedData.barangays[cityId] = data;
                populateDropdown(barangayDropdown, data);
            })
            .catch(error => {
                console.error('Error fetching barangays:', error);
                barangayDropdown.innerHTML = '<option value="">Error loading</option>';
            });
    });

    // Load initial values if in edit mode
    if (isEditMode) {
        // Enable dropdowns only if their parent has a value
        provinceDropdown.disabled = !initialValues.region;
        cityDropdown.disabled = !initialValues.province;
        barangayDropdown.disabled = !initialValues.city;

        if (initialValues.region) {
            fetch('/locations/regions/')
                .then(res => res.json())
                .then(data => {
                    populateDropdown(regionDropdown, data, initialValues.region);
                    regionsLoaded = true;
                    return initialValues.region ? fetch(`/locations/provinces/${initialValues.region}/`) : null;
                })
                .then(res => res ? res.json() : null)
                .then(data => {
                    if (data) {
                        cachedData.provinces[initialValues.region] = data;
                        populateDropdown(provinceDropdown, data, initialValues.province);
                        return initialValues.province ? fetch(`/locations/cities/${initialValues.province}/`) : null;
                    }
                })
                .then(res => res ? res.json() : null)
                .then(data => {
                    if (data) {
                        cachedData.cities[initialValues.province] = data;
                        populateDropdown(cityDropdown, data, initialValues.city);
                        return initialValues.city ? fetch(`/locations/barangays/${initialValues.city}/`) : null;
                    }
                })
                .then(res => res ? res.json() : null)
                .then(data => {
                    if (data) {
                        cachedData.barangays[initialValues.city] = data;
                        populateDropdown(barangayDropdown, data, initialValues.barangay);
                    }
                })
                .catch(error => {
                    console.error('Error loading initial data:', error);
                });
        }
    }

    const form = document.querySelector('form'); // adjust selector if needed

    form.addEventListener('submit', function() {
        [regionDropdown, provinceDropdown, cityDropdown, barangayDropdown].forEach(dropdown => {
            if (dropdown.value && !dropdown.querySelector(`option[value="${dropdown.value}"]`)) {
                const opt = document.createElement('option');
                opt.value = dropdown.value;
                opt.textContent = dropdown.dataset.name || 'Selected'; // optional: store display name in data-name
                opt.selected = true;
                dropdown.appendChild(opt);
            }
        });
    });

});
