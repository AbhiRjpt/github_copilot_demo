describe('Activity Signup App', () => {
    let activitiesList, activitySelect, signupForm, messageDiv;

    beforeEach(() => {
        document.body.innerHTML = `
            <div id="activities-list"></div>
            <select id="activity"></select>
            <form id="signup-form">
                <input id="email" type="email" value="test@example.com">
                <button type="submit">Sign Up</button>
            </form>
            <div id="message" class="hidden"></div>
        `;
        activitiesList = document.getElementById('activities-list');
        activitySelect = document.getElementById('activity');
        signupForm = document.getElementById('signup-form');
        messageDiv = document.getElementById('message');
    });

    describe('fetchActivities', () => {
        test('should fetch and display activities', async () => {
            const mockActivities = {
                'Yoga': { description: 'Relaxing yoga', schedule: 'Monday 10am', max_participants: 20, participants: [] },
                'Running': { description: 'Morning run', schedule: 'Tuesday 6am', max_participants: 15, participants: ['user1'] }
            };
            global.fetch = jest.fn(() => Promise.resolve({ json: () => Promise.resolve(mockActivities) }));

            await fetchActivities();

            expect(activitiesList.children.length).toBe(2);
            expect(activitySelect.children.length).toBe(2);
        });

        test('should handle fetch errors', async () => {
            global.fetch = jest.fn(() => Promise.reject(new Error('Network error')));
            await fetchActivities();
            expect(activitiesList.innerHTML).toContain('Failed to load activities');
        });
    });

    describe('form submission', () => {
        test('should submit signup and show success message', async () => {
            global.fetch = jest.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ message: 'Signed up!' }) }));
            signupForm.dispatchEvent(new Event('submit'));
            await new Promise(resolve => setTimeout(resolve, 100));
            expect(messageDiv.textContent).toBe('Signed up!');
            expect(messageDiv.className).toBe('success');
        });

        test('should show error message on failed signup', async () => {
            global.fetch = jest.fn(() => Promise.resolve({ ok: false, json: () => Promise.resolve({ detail: 'Activity full' }) }));
            signupForm.dispatchEvent(new Event('submit'));
            await new Promise(resolve => setTimeout(resolve, 100));
            expect(messageDiv.className).toBe('error');
        });
    });
});